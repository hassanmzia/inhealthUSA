<?php

namespace App\Http\Controllers;

use App\Models\Prescription;
use App\Models\Encounter;
use App\Models\Patient;
use App\Models\Provider;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\View\View;

class PrescriptionController extends Controller
{
    /**
     * Display a listing of prescriptions
     */
    public function index(Request $request): View
    {
        $query = Prescription::with(['patient', 'provider']);

        // Filter by status
        if ($request->has('status')) {
            $query->where('status', $request->input('status'));
        }

        // Filter by patient
        if ($request->has('patient_id')) {
            $query->where('patient_id', $request->input('patient_id'));
        }

        $prescriptions = $query->orderBy('prescribed_date', 'desc')->paginate(20);

        return view('prescriptions.index', compact('prescriptions'));
    }

    /**
     * Show the form for creating a new prescription
     */
    public function create(Request $request): View
    {
        $patients = Patient::orderBy('last_name')->orderBy('first_name')->get();
        $providers = Provider::active()->orderBy('last_name')->get();
        $encounters = Encounter::with('patient')->orderBy('encounter_date', 'desc')->limit(100)->get();

        return view('prescriptions.create', compact('patients', 'providers', 'encounters'));
    }

    /**
     * Store a newly created prescription
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'patient_id' => 'required|exists:patients,patient_id',
            'provider_id' => 'required|exists:providers,provider_id',
            'encounter_id' => 'nullable|exists:encounters,encounter_id',
            'medication_name' => 'required|string|max:300',
            'dosage' => 'required|string|max:200',
            'frequency' => 'required|string|max:200',
            'duration' => 'nullable|string|max:200',
            'quantity' => 'nullable|integer',
            'refills' => 'nullable|integer',
            'route' => 'nullable|string|max:100',
            'instructions' => 'nullable|string',
            'pharmacy_name' => 'nullable|string|max:200',
            'pharmacy_address' => 'nullable|string|max:500',
            'pharmacy_phone' => 'nullable|string|max:20',
            'start_date' => 'nullable|date',
            'end_date' => 'nullable|date',
            'status' => 'required|in:Active,Pending,Completed,Discontinued',
            'notes' => 'nullable|string',
        ]);

        $validated['prescribed_date'] = now();

        $prescription = Prescription::create($validated);

        return redirect()
            ->route('prescriptions.show', $prescription->prescription_id)
            ->with('success', 'Prescription created successfully.');
    }

    /**
     * Display the specified prescription
     */
    public function show(Prescription $prescription): View
    {
        $prescription->load(['patient', 'provider', 'encounter']);

        return view('prescriptions.show', compact('prescription'));
    }

    /**
     * Show the form for editing the specified prescription
     */
    public function edit(Prescription $prescription): View
    {
        return view('prescriptions.edit', compact('prescription'));
    }

    /**
     * Update the specified prescription
     */
    public function update(Request $request, Prescription $prescription): RedirectResponse
    {
        $validated = $request->validate([
            'medication_name' => 'required|string|max:300',
            'dosage' => 'required|string|max:200',
            'frequency' => 'required|string|max:200',
            'duration' => 'nullable|string|max:200',
            'quantity' => 'nullable|integer',
            'refills' => 'nullable|integer',
            'route' => 'nullable|string|max:100',
            'instructions' => 'nullable|string',
            'status' => 'required|in:Active,Completed,Discontinued,Cancelled',
            'notes' => 'nullable|string',
        ]);

        $prescription->update($validated);

        return redirect()
            ->route('prescriptions.show', $prescription->prescription_id)
            ->with('success', 'Prescription updated successfully.');
    }

    /**
     * Discontinue a prescription
     */
    public function discontinue(Prescription $prescription): RedirectResponse
    {
        $prescription->update(['status' => 'Discontinued']);

        return redirect()
            ->route('prescriptions.show', $prescription->prescription_id)
            ->with('success', 'Prescription discontinued successfully.');
    }
}
