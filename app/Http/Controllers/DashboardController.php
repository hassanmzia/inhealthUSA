<?php

namespace App\Http\Controllers;

use App\Models\Patient;
use App\Models\Encounter;
use App\Models\Provider;
use App\Models\Department;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    /**
     * Display the application dashboard
     */
    public function index(): View
    {
        // Statistics
        $stats = [
            'total_patients' => Patient::active()->count(),
            'active_encounters' => Encounter::active()->count(),
            'total_providers' => Provider::active()->count(),
            'todays_appointments' => Encounter::whereDate('encounter_date', today())->count(),
        ];

        // Recent encounters
        $recentEncounters = Encounter::with(['patient', 'provider', 'department'])
            ->orderBy('encounter_date', 'desc')
            ->limit(10)
            ->get();

        // Active encounters by status
        $encountersByStatus = Encounter::select('status', DB::raw('count(*) as count'))
            ->whereIn('status', ['Scheduled', 'In Progress'])
            ->groupBy('status')
            ->get()
            ->pluck('count', 'status');

        // Encounters by department (today)
        $encountersByDepartment = Encounter::with('department')
            ->whereDate('encounter_date', today())
            ->get()
            ->groupBy('department.department_name')
            ->map(function ($group) {
                return $group->count();
            });

        // Critical alerts (patients with severe allergies)
        $criticalAllergies = Patient::with('allergies')
            ->whereHas('allergies', function ($query) {
                $query->active()
                    ->whereIn('severity', ['Severe', 'Life-threatening']);
            })
            ->limit(5)
            ->get();

        return view('dashboard', compact(
            'stats',
            'recentEncounters',
            'encountersByStatus',
            'encountersByDepartment',
            'criticalAllergies'
        ));
    }
}
