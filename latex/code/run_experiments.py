#!/usr/bin/env python3
"""Reproduce the four experiments in Chapter 9.

The water-filling CVXPY model and the fixed-target SINR feasibility model are
adapted from CVXPY Developers, cvxpy/examples, commit
73a6892ef5bea4ded68f8f9fab17e48119dc62f5:
notebooks/WWW/water_filling_BVex5.2.ipynb and
notebooks/WWW/maximise_minimum_SINR_BV4.20.ipynb.
Original notebook authors: R. Gowers, S. Al-Izzi, T. Pollington, R. Hill, K. Briggs.
Copyright attribution: CVXPY Developers / upstream notebook contributors.
Licensed under Apache-2.0; see ../third_party/cvxpy-examples/LICENSE.
Modified for this textbook, November 2026: new deterministic parameters;
physical log2 rate; exact formulas and independent residual checks; direct
unnormalized power constraints; additional figures and tabulated diagnostics.
WMMSE and ISTA implementations below are newly written for this textbook.
"""
from pathlib import Path
import csv
import json
import platform
import numpy as np
import scipy
from scipy.linalg import eigvalsh
import cvxpy as cp
import clarabel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
DATA = ROOT / 'data'
for d in (FIG, DATA): d.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': .22,
                     'pdf.fonttype': 42, 'savefig.bbox': 'tight'})
OPTIONS = dict(solver='CLARABEL', tol_gap_abs=1e-10, tol_gap_rel=1e-10,
               tol_feas=1e-10, max_iter=300)


def savefig(fig, name):
    fig.savefig(FIG / (name + '.pdf'))
    fig.savefig(FIG / (name + '.png'), dpi=180)
    plt.close(fig)


def writecsv(name, headers, rows):
    with open(DATA / name, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(rows)


def water_filling():
    alpha = np.array([1., 2., 4., 8.]); P = 10.
    lo, hi = 0., float(alpha.max()+P)
    while hi-lo > 1e-12:
        mid = (lo+hi)/2
        if np.maximum(mid-alpha, 0).sum() > P: hi = mid
        else: lo = mid
    mu = (lo+hi)/2
    exact = np.maximum(mu-alpha, 0)
    # Adapted CVXPY formulation: same sum-log model, physical log2 rate.
    p = cp.Variable(4, nonneg=True)
    problem = cp.Problem(cp.Maximize(cp.sum(cp.log1p(cp.multiply(1/alpha,p)))/np.log(2)),
                         [cp.sum(p) <= P])
    problem.solve(**OPTIONS)
    numeric = np.maximum(np.asarray(p.value), 0)
    rate = float(np.log2(1+exact/alpha).sum())
    uniform_rate = float(np.log2(1+(P/4)/alpha).sum())
    error = float(np.max(np.abs(exact-numeric)))
    assert problem.status == 'optimal'
    assert error < 1e-3 and abs(exact.sum()-P) < 1e-9
    fig, ax = plt.subplots(figsize=(6.7,3.5))
    x=np.arange(1,5)
    ax.bar(x, alpha, color='#aab7c4', label=r'Equivalent noise $\alpha_n$')
    ax.bar(x, exact, bottom=alpha, color='#2683a6', label=r'Allocated power $p_n$')
    ax.axhline(mu, color='#bb4d28', linestyle='--', label=rf'Water level $\mu={mu:.4f}$')
    ax.set(xlabel='Parallel channel index', ylabel='Normalized power', xticks=x, ylim=(0,9))
    ax.legend(fontsize=9, loc='upper left')
    savefig(fig, 'water_filling')
    writecsv('water_filling.csv', ['channel','alpha','p_exact','p_cvxpy'],
             zip(x,alpha,exact,numeric))
    return dict(alpha=alpha.tolist(), P=P, water_level=mu, p=exact.tolist(),
                cvxpy_p=numeric.tolist(), max_allocation_error=error,
                rate_bit_s_Hz=rate, uniform_rate_bit_s_Hz=uniform_rate,
                cvxpy_status=problem.status, per_channel_bandwidth_Hz=1.0,
                total_rate_bit_s=rate, aggregate_spectral_efficiency_bit_s_Hz=rate/4)


def power_control():
    G=np.array([[1,.15,.1],[.2,1,.15],[.1,.2,1.]])
    noise=np.full(3,.1); caps=np.ones(3); total_cap=2.
    D=np.diag(G); off=G-np.diag(D)
    def formula(gamma):
        F=gamma*off/D[:,None]; eta=gamma*noise/D
        rho=float(np.max(np.abs(np.linalg.eigvals(F))))
        if rho >= 1: return rho, None
        return rho,np.linalg.solve(np.eye(3)-F,eta)
    def residual(p,gamma):
        return float(max(0,np.max(gamma*(off@p+noise)-D*p),
                         np.max(-p),np.max(p-caps),p.sum()-total_cap))
    target=2.
    rho,pstar=formula(target)
    # Adapted from the upstream SINR notebook. Power constraints here retain
    # their physical values; there is no row normalization of group budgets.
    p=cp.Variable(3, nonneg=True)
    gam=cp.Parameter(nonneg=True, value=target)
    problem=cp.Problem(cp.Minimize(cp.sum(p)),
                        [gam*(off@p+noise) <= cp.multiply(D,p),
                         p <= caps, cp.sum(p) <= total_cap])
    problem.solve(**OPTIONS)
    lp=np.array(p.value)
    assert problem.status == 'optimal'
    assert np.max(np.abs(lp-pstar)) < 1e-7
    assert residual(lp,target) < 1e-8
    lo=0.; hi=float(np.min(D*caps/noise))
    initial_upper=hi
    steps=0
    while hi-lo > 1e-8:
        mid=(lo+hi)/2; _, pp=formula(mid)
        if pp is not None and np.all(pp <= caps) and pp.sum() <= total_cap:
            lo=mid
        else: hi=mid
        steps+=1
    _,pmax=formula(lo)
    gam.value=lo-1e-3
    problem.solve(**OPTIONS)
    assert problem.status == 'optimal'
    gam.value=hi+1e-3
    problem.solve(**OPTIONS)
    assert problem.status == 'infeasible'
    actual=D*pmax/(off@pmax+noise)
    gammas=np.linspace(0,6,301)
    rows=[]
    for g in gammas:
        r,pp=formula(g)
        rows.append([g,r,np.nan if pp is None else pp.sum(),
                     0 if pp is None else int(np.all(pp<=caps) and pp.sum()<=total_cap)])
    arr=np.array(rows)
    fig,axs=plt.subplots(1,2,figsize=(8.7,3.5))
    axs[0].plot(arr[:,0],arr[:,2],color='#2683a6',label='Minimum sum power')
    axs[0].axhline(total_cap,color='#bb4d28',ls='--',label='Sum-power budget')
    axs[0].axvline(lo,color='#34495e',ls=':',label=rf'Max-min target $={lo:.4f}$')
    axs[0].set(xlabel=r'Target SINR $\gamma$',ylabel='Normalized power',ylim=(0,4))
    axs[0].legend(fontsize=8)
    axs[1].plot(arr[:,0],arr[:,1],color='#2683a6',label=r'Spectral radius $\rho(F)$')
    axs[1].axhline(1,color='#bb4d28',ls='--',label=r'$\rho(F)=1$')
    axs[1].axvline(lo,color='#34495e',ls=':')
    axs[1].set(xlabel=r'Target SINR $\gamma$',ylabel='Spectral radius')
    axs[1].legend(fontsize=8)
    savefig(fig,'power_control')
    writecsv('power_control_scan.csv', ['gamma','rho','minimum_sum_power','feasible'],rows)
    return dict(G=G.tolist(),noise=noise.tolist(),peak_caps=caps.tolist(),
                total_cap=total_cap,target_gamma=target,rho_at_target=rho,
                p_exact=pstar.tolist(),p_lp=lp.tolist(),
                lp_error=float(np.max(np.abs(lp-pstar))),lp_residual=residual(lp,target),
                maxmin_lower=lo,maxmin_upper=hi,bisection_steps=steps,
                initial_upper=initial_upper,maxmin_p=pmax.tolist(),
                maxmin_sinr=actual.tolist(),maxmin_residual=residual(pmax,lo))


def wmmse():
    H=np.array([[1,.8,.3],[.7,1,.6],[.4,.5,1.]])
    g=H**2; noise=.2; P=3.; rng=np.random.default_rng(7)
    def rate(v):
        p=v*v; signal=np.diag(g)*p
        return float(np.log2(1+signal/(g@p-signal+noise)).sum())
    def update(v):
        T=g@(v*v)+noise
        u=np.diag(H)*v/T
        e=1-2*u*np.diag(H)*v+u*u*T
        q=1/e
        numer=q*u*np.diag(H)
        denom=(q*u*u)@g
        def trial(lam): return numer/(denom+lam)
        if np.sum(trial(0)**2) <= P: return trial(0)
        lo,hi=0.,1.
        while np.sum(trial(hi)**2)>P: hi*=2
        for _ in range(80):
            mid=(lo+hi)/2
            if np.sum(trial(mid)**2)>P: lo=mid
            else: hi=mid
        return trial(hi)
    random=rng.uniform(.1,1,3); random=np.sqrt(P)*random/np.linalg.norm(random)
    initials={'Equal power':np.ones(3), 'Random seed 7':random,
              'User 2 biased':np.sqrt(np.array([.01,2.98,.01]))}
    results={}; traces={}
    for name,v0 in initials.items():
        v=v0.copy(); hist=[rate(v)]
        for it in range(3000):
            vnew=update(v); hist.append(rate(vnew)); v=vnew
            if abs(hist[-1]-hist[-2]) <= 1e-10*max(1,abs(hist[-1])): break
        trace=np.array(hist)
        assert np.min(np.diff(trace)) > -1e-10
        assert np.sum(v*v) <= P+1e-10
        traces[name]=trace
        results[name]=dict(iterations=len(hist)-1,initial_rate=hist[0],
                           final_rate=hist[-1],power=(v*v).tolist(),
                           min_rate_increment=float(np.min(np.diff(trace))))
    grid_step=.02; n=int(round(P/grid_step)); best=(-np.inf,None)
    # At least one nonzero power is needed at an optimum. A common increase
    # in all nonzero powers strictly improves every active SINR when noise>0,
    # so a sum-power constrained sum-rate optimum uses the full P.
    for i in range(n+1):
        for j in range(n-i+1):
            pp=grid_step*np.array([i,j,n-i-j],float)
            rr=rate(np.sqrt(pp))
            if rr>best[0]: best=(rr,pp.copy())
    fig,ax=plt.subplots(figsize=(6.7,3.7))
    colors=['#2683a6','#bb4d28','#6554a0']
    for (name,trace),color in zip(traces.items(),colors):
        ax.plot(np.arange(len(trace)),trace,label=name,color=color)
    ax.axhline(best[0],ls='--',color='#58646e',label='Best feasible grid point')
    ax.set(xlabel='WMMSE iteration',ylabel='Sum rate [bit/s/Hz]')
    ax.legend(fontsize=8)
    savefig(fig,'wmmse')
    rows=[]
    for name,trace in traces.items():
        rows.extend([[name,i,r] for i,r in enumerate(trace)])
    writecsv('wmmse_history.csv',['initialization','iteration','sum_rate_bit_s_Hz'],rows)
    return dict(H=H.tolist(),noise=noise,total_power=P,initializations=results,
                grid_step=grid_step,grid_best_rate=best[0],grid_best_power=best[1].tolist(),
                grid_point_count=(n+1)*(n+2)//2)


def lasso():
    rng=np.random.default_rng(7)
    A=rng.normal(size=(40,80)); A/=np.linalg.norm(A,axis=0)
    support=np.sort(rng.choice(80,5,replace=False))
    truth=np.zeros(80); truth[support]=np.array([1.2,-.8,.6,1.,-.9])
    y=A@truth+.02*rng.normal(size=40)
    lam=.06; L=float(np.linalg.norm(A,2)**2)
    def objective(x): return float(.5*np.linalg.norm(A@x-y)**2+lam*np.linalg.norm(x,1))
    def shrink(x,tau): return np.sign(x)*np.maximum(np.abs(x)-tau,0)
    x=np.zeros(80); hist=[objective(x)]
    for it in range(20000):
        z=x-A.T@(A@x-y)/L; xn=shrink(z,lam/L)
        hist.append(objective(xn)); x=xn
        if np.linalg.norm(L*(x-shrink(x-A.T@(A@x-y)/L,lam/L)),np.inf) < 1e-8:
            break
    xc=cp.Variable(80)
    problem=cp.Problem(cp.Minimize(.5*cp.sum_squares(A@xc-y)+lam*cp.norm1(xc)))
    problem.solve(**OPTIONS)
    assert problem.status == 'optimal'
    gap=objective(x)-float(problem.value)
    assert abs(gap) < 1e-7
    assert np.min(-np.diff(hist)) > -1e-10
    pg=float(np.linalg.norm(L*(x-shrink(x-A.T@(A@x-y)/L,lam/L)),np.inf))
    fig,axs=plt.subplots(1,2,figsize=(8.8,3.5))
    gaps=np.maximum(np.array(hist)-problem.value,1e-12)
    axs[0].semilogy(np.arange(len(hist)),gaps,color='#2683a6')
    axs[0].set(xlabel='ISTA iteration',ylabel='Objective minus CVXPY optimum')
    axs[1].plot(truth,'o',ms=4,label='True channel',color='#bb4d28')
    axs[1].plot(x,'x',ms=4,label='LASSO estimate',color='#2683a6')
    axs[1].set(xlabel='Channel coefficient index (0-based)',ylabel='Coefficient')
    axs[1].legend(fontsize=8, loc='upper center', bbox_to_anchor=(.5,1.2), ncol=2)
    savefig(fig,'lasso')
    writecsv('lasso_history.csv',['iteration','objective'],enumerate(hist))
    writecsv('lasso_coefficients.csv',['index','truth','ista','cvxpy'],zip(range(80),truth,x,xc.value))
    np.savez(DATA/'lasso_input.npz',A=A,y=y,truth=truth,lambda_=lam)
    return dict(seed=7,shape=[40,80],support_zero_based=support.tolist(),noise_std=.02,
                lambda_=lam,L=L,iterations=len(hist)-1,objective_ista=hist[-1],
                objective_cvxpy=float(problem.value),objective_gap=gap,
                proximal_gradient_inf=pg,relative_estimation_error=float(np.linalg.norm(x-truth)/np.linalg.norm(truth)))


def main():
    results={'versions':{'python':platform.python_version(),'numpy':np.__version__,
                        'scipy':scipy.__version__,'cvxpy':cp.__version__,'clarabel':clarabel.__version__,
                        'matplotlib':matplotlib.__version__},
             'solver':'CLARABEL','solver_options':OPTIONS,
             'water_filling':water_filling(),'power_control':power_control(),
             'wmmse':wmmse(),'lasso':lasso()}
    (DATA/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
