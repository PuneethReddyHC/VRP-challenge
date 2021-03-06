from django.shortcuts import render
from django.http import HttpResponse

from .models import VrpPoint, VrpProblem, RoutingPlan

import json
import sys
from .vrp_solver import solve_vrp
from .vrp_solver.misc import distance_diff


def index(request):
    return render(request, 'vrp/index.html')


def create_problem(request):

    context = {}
    try:
        context['depot_id'] = request.POST['depot_id']
        context['problem_name'] = request.POST['problem_name']
        context['status'] = 'OK'

        # if request.POST['dataset'] == "Create new":
        #     print('redirect')
        # else:
        try:
            problem = VrpProblem(name=request.POST['problem_name'],
                                 depot_id=request.POST['depot_id'])
            problem.save()
        except:
            context['status'] = 'Problem is NOT created! Error: ' + \
                str(sys.exc_info()[0])
            return render(request, 'vrp/index.html', context=context)

        try:
            vrp_points = request.POST['vrp_points'].split(';')[0:-1]    # Last point is empty.   
            p_id = 0
            for p in vrp_points:
                point = VrpPoint(problem=VrpProblem.objects.get(name=request.POST['problem_name']),
                                 lat=float(p.split(',')[0]),
                                 lon=float(p.split(',')[1]),
                                 poind_id=p_id)
                p_id += 1
                point.save()
           
        except:
            context['status'] = 'VRP points are NOT created! Error: ' + \
                str(sys.exc_info()[0])
            return render(request, 'vrp/index.html', context=context)

    except:
        context['status'] = 'Exception!'
        return render(request, 'vrp/index.html', context=context)

    vrp_problem = VrpProblem.objects.all()    
    context['vrp_problems'] = vrp_problem

    return render(request, 'vrp/problem_setting.html', context=context)


def problem_setting(request):
    context = {}    
    vrp_problem = VrpProblem.objects.all()    
    context['vrp_problems'] = vrp_problem
    return render(request, 'vrp/problem_setting.html', context=context)


def problem_solution(request):
    context = {}
    context['problem_name'] = request.POST['problem_name']
    lsm = request.POST['lsm']
    ffs = request.POST['ffs']
    n_veh = request.POST['n_veh']    
    context['lsm'] = lsm    
    context['ffs'] = ffs
    context['n_veh'] = n_veh
    
    try:
        problem = VrpProblem.objects.get(name=request.POST['problem_name'])

        vrp_points = list(VrpPoint.objects.filter(problem_id=problem.id))
        if len(vrp_points) == 0:
            context['status'] = 'Error: There are no VrpPoints defined!'
            return render(request, 'vrp/problem_solution.html', context=context)

        
        # if len(routing_rez) > 0:  # if solution exists, do not run VRP.
            
        #     context['status'] = 'Error: Solution for this problem already exists!'
        #     return render(request, 'vrp/problem_solution.html', context=context)
       
        
        string_rez, dict_rez = solve_vrp(
            vrp_points=vrp_points, 
            problem_id=problem.id, 
            depot_id=problem.depot_id,
            ffs=ffs,
            lsm=lsm,
            n_veh=int(n_veh))
        routing_rez = list(RoutingPlan.objects.filter(problem_id=problem.id,vehicle_num=int(n_veh)))
        context['string_rez'] = string_rez
        context['status'] = 'OK'


        input_matrix = []
        for point in vrp_points:
            input_matrix.append(
                (
                    int(point.poind_id),
                    float(point.lat),
                    float(point.lon)
                )
            )

        locations = []
        for r_r in routing_rez:
            route = [int(p) for p in r_r.routing_plan.split(';')]
            temp = []
            for r in route:
                for i in input_matrix:
                    if r == i[0]:
                        temp.append([i[1], i[2]])
            locations.append(temp)
        context['data'] = json.dumps(locations)

    except Exception as e:
        
        context['status'] = 'Something went wrong! Error: ' + \
            str(sys.exc_info()[0]) + ' ' + str(e)
        return render(request, 'vrp/problem_solution.html', context=context)

    else:
        return render(request, 'vrp/problem_solution.html', context=context)

