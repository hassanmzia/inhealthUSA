<?php

namespace App\Http\Controllers;

use App\Models\Encounter;
use App\Models\Patient;
use App\Models\Provider;
use App\Models\Department;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Illuminate\Http\RedirectResponse;

class AppointmentController extends Controller
{
    /**
     * Display a listing of appointments
     */
    public function index(Request $request): View
    {
        $query = Encounter::with(['patient', 'provider', 'department']);

        // Filter by status
        if ($request->has('status')) {
            $query->where('status', $request->input('status'));
        }

        // Filter by date
        if ($request->has('date')) {
            $query->whereDate('encounter_date', $request->input('date'));
        }

        $encounters = $query->orderBy('encounter_date', 'desc')->paginate(20);

        return view('appointments.index', compact('encounters'));
    }

    /**
     * Show the form for creating a new appointment
     */
    public function create(Request $request): View
    {
        $patients = Patient::orderBy('last_name')->orderBy('first_name')->get();
        $providers = Provider::active()->orderBy('last_name')->get();
        $departments = Department::active()->orderBy('department_name')->get();

        return view('appointments.create', compact('patients', 'providers', 'departments'));
    }

    /**
     * Store a newly created appointment
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'patient_id' => 'required|exists:patients,patient_id',
            'provider_id' => 'required|exists:providers,provider_id',
            'encounter_date' => 'required|date',
            'encounter_type' => 'required|in:Inpatient,Outpatient,Emergency,Telehealth,Follow-up',
            'department_id' => 'required|exists:departments,department_id',
            'status' => 'nullable|in:Scheduled,In Progress,Completed,Cancelled',
        ]);

        $validated['status'] = $validated['status'] ?? 'In Progress';

        $encounter = Encounter::create($validated);

        return redirect()
            ->route('appointments.show', $encounter->encounter_id)
            ->with('success', 'Appointment created successfully.');
    }

    /**
     * Display the specified appointment
     */
    public function show(Encounter $encounter): View
    {
        $encounter->load([
            'patient',
            'provider',
            'department',
            'chiefComplaints',
            'vitalSigns',
            'diagnoses.diagnosingProvider',
            'prescriptions',
            'physicalExamination',
            'clinicalImpression',
            'treatmentPlan'
        ]);

        return view('appointments.show', compact('encounter'));
    }

    /**
     * Show the form for editing the specified appointment
     */
    public function edit(Encounter $encounter): View
    {
        $providers = Provider::active()->orderBy('last_name')->get();
        $departments = Department::active()->orderBy('department_name')->get();

        return view('appointments.edit', compact('encounter', 'providers', 'departments'));
    }

    /**
     * Update the specified appointment
     */
    public function update(Request $request, Encounter $encounter): RedirectResponse
    {
        $validated = $request->validate([
            'provider_id' => 'required|exists:providers,provider_id',
            'encounter_date' => 'required|date',
            'encounter_type' => 'required|in:Inpatient,Outpatient,Emergency,Telehealth,Follow-up',
            'department_id' => 'required|exists:departments,department_id',
            'status' => 'required|in:Scheduled,In Progress,Completed,Cancelled',
        ]);

        $encounter->update($validated);

        return redirect()
            ->route('appointments.show', $encounter->encounter_id)
            ->with('success', 'Appointment updated successfully.');
    }

    /**
     * Complete an appointment
     */
    public function complete(Encounter $encounter): RedirectResponse
    {
        $encounter->update(['status' => 'Completed']);

        return redirect()
            ->route('appointments.show', $encounter->encounter_id)
            ->with('success', 'Appointment completed successfully.');
    }
}
