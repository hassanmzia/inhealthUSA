<?php

namespace App\Http\Controllers;

use App\Models\Prescription;
use App\Models\Encounter;
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
    public function create(Encounter $encounter): View
    {
        return view('prescriptions.create', compact('encounter'));
    }

    /**
     * Store a newly created prescription
     */
    public function store(Request $request, Encounter $encounter): RedirectResponse
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
            'pharmacy_name' => 'nullable|string|max:200',
            'pharmacy_address' => 'nullable|string|max:500',
            'pharmacy_phone' => 'nullable|string|max:20',
            'start_date' => 'nullable|date',
            'end_date' => 'nullable|date',
            'notes' => 'nullable|string',
        ]);

        $validated['encounter_id'] = $encounter->encounter_id;
        $validated['patient_id'] = $encounter->patient_id;
        $validated['provider_id'] = $encounter->provider_id;
        $validated['prescribed_date'] = now();
        $validated['status'] = 'Active';

        Prescription::create($validated);

        return redirect()
            ->route('encounters.show', $encounter->encounter_id)
            ->with('success', 'Prescription added successfully.');
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
