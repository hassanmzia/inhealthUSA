<?php

namespace App\Http\Controllers;

use App\Models\Diagnosis;
use App\Models\Encounter;
use App\Models\Provider;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\View\View;

class DiagnosisController extends Controller
{
    /**
     * Show the form for adding a diagnosis to an encounter
     */
    public function create(Encounter $encounter): View
    {
        $providers = Provider::active()->orderBy('last_name')->orderBy('first_name')->get();
        return view('diagnoses.create', compact('encounter', 'providers'));
    }

    /**
     * Store a diagnosis for an encounter
     */
    public function store(Request $request, Encounter $encounter): RedirectResponse
    {
        $validated = $request->validate([
            'diagnosis_description' => 'required|string',
            'icd10_code' => 'nullable|string|max:20',
            'icd11_code' => 'nullable|string|max:20',
            'diagnosis_type' => 'required|in:Primary,Secondary,Differential',
            'status' => 'nullable|in:Active,Resolved,Rule Out',
            'onset_date' => 'nullable|date',
            'notes' => 'nullable|string',
        ]);

        $validated['encounter_id'] = $encounter->encounter_id;
        $validated['diagnosed_by'] = auth()->user()->id ?? 1; // Default to 1 if no auth
        $validated['status'] = $validated['status'] ?? 'Active';

        Diagnosis::create($validated);

        return redirect()
            ->route('appointments.show', $encounter->encounter_id)
            ->with('success', 'Diagnosis added successfully.');
    }

    /**
     * Show the form for editing a diagnosis
     */
    public function edit(Diagnosis $diagnosis): View
    {
        $providers = Provider::active()->orderBy('last_name')->orderBy('first_name')->get();
        $encounter = $diagnosis->encounter;
        return view('diagnoses.edit', compact('diagnosis', 'providers', 'encounter'));
    }

    /**
     * Update a diagnosis
     */
    public function update(Request $request, Diagnosis $diagnosis): RedirectResponse
    {
        $validated = $request->validate([
            'diagnosis_description' => 'required|string',
            'icd10_code' => 'nullable|string|max:20',
            'icd11_code' => 'nullable|string|max:20',
            'diagnosis_type' => 'required|in:Primary,Secondary,Differential',
            'status' => 'required|in:Active,Resolved,Rule Out',
            'onset_date' => 'nullable|date',
            'resolved_date' => 'nullable|date',
            'notes' => 'nullable|string',
        ]);

        $diagnosis->update($validated);

        return redirect()
            ->route('appointments.show', $diagnosis->encounter_id)
            ->with('success', 'Diagnosis updated successfully.');
    }

    /**
     * Remove a diagnosis
     */
    public function destroy(Diagnosis $diagnosis): RedirectResponse
    {
        $encounterId = $diagnosis->encounter_id;
        $diagnosis->delete();

        return redirect()
            ->route('appointments.show', $encounterId)
            ->with('success', 'Diagnosis removed successfully.');
    }
}
