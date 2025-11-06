<?php

namespace App\Http\Controllers;

use App\Models\Patient;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Illuminate\Http\RedirectResponse;

class PatientController extends Controller
{
    /**
     * Display a listing of patients
     */
    public function index(Request $request): View
    {
        $query = Patient::with(['insurance', 'emergencyContacts'])
            ->active();

        // Search functionality
        if ($request->has('search')) {
            $search = $request->input('search');
            $query->where(function($q) use ($search) {
                $q->where('first_name', 'like', "%{$search}%")
                  ->orWhere('last_name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%")
                  ->orWhere('phone_number', 'like', "%{$search}%");
            });
        }

        $patients = $query->orderBy('last_name')->paginate(20);

        return view('patients.index', compact('patients'));
    }

    /**
     * Show the form for creating a new patient
     */
    public function create(): View
    {
        return view('patients.create');
    }

    /**
     * Store a newly created patient
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'first_name' => 'required|string|max:100',
            'last_name' => 'required|string|max:100',
            'middle_name' => 'nullable|string|max:100',
            'date_of_birth' => 'required|date',
            'gender' => 'required|in:Male,Female,Other,Unknown',
            'address_street' => 'nullable|string|max:255',
            'address_city' => 'nullable|string|max:100',
            'address_state' => 'nullable|string|max:50',
            'address_zip' => 'nullable|string|max:20',
            'phone_number' => 'nullable|string|max:20',
            'email' => 'nullable|email|max:255',
        ]);

        $patient = Patient::create($validated);

        return redirect()
            ->route('patients.show', $patient->patient_id)
            ->with('success', 'Patient created successfully.');
    }

    /**
     * Display the specified patient
     */
    public function show(Patient $patient): View
    {
        $patient->load([
            'encounters.provider',
            'encounters.department',
            'allergies',
            'prescriptions.provider',
            'pastMedicalHistory',
            'surgicalHistory',
            'familyHistory',
            'socialHistory',
            'insurance',
            'emergencyContacts'
        ]);

        return view('patients.show', compact('patient'));
    }

    /**
     * Show the form for editing the specified patient
     */
    public function edit(Patient $patient): View
    {
        return view('patients.edit', compact('patient'));
    }

    /**
     * Update the specified patient
     */
    public function update(Request $request, Patient $patient): RedirectResponse
    {
        $validated = $request->validate([
            'first_name' => 'required|string|max:100',
            'last_name' => 'required|string|max:100',
            'middle_name' => 'nullable|string|max:100',
            'date_of_birth' => 'required|date',
            'gender' => 'required|in:Male,Female,Other,Unknown',
            'address_street' => 'nullable|string|max:255',
            'address_city' => 'nullable|string|max:100',
            'address_state' => 'nullable|string|max:50',
            'address_zip' => 'nullable|string|max:20',
            'phone_number' => 'nullable|string|max:20',
            'email' => 'nullable|email|max:255',
        ]);

        $patient->update($validated);

        return redirect()
            ->route('patients.show', $patient->patient_id)
            ->with('success', 'Patient updated successfully.');
    }

    /**
     * Remove the specified patient (soft delete)
     */
    public function destroy(Patient $patient): RedirectResponse
    {
        $patient->update(['is_active' => false]);

        return redirect()
            ->route('patients.index')
            ->with('success', 'Patient deactivated successfully.');
    }
}
