<?php

namespace App\Http\Controllers;

use App\Models\VitalSign;
use App\Models\Encounter;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\View\View;

class VitalSignController extends Controller
{
    /**
     * Show the form for adding vital signs to an encounter
     */
    public function create(Encounter $encounter): View
    {
        return view('vital-signs.create', compact('encounter'));
    }

    /**
     * Store vital signs for an encounter
     */
    public function store(Request $request, Encounter $encounter): RedirectResponse
    {
        $validated = $request->validate([
            'temperature_value' => 'nullable|numeric|between:90,110',
            'temperature_unit' => 'nullable|in:C,F',
            'blood_pressure_systolic' => 'nullable|integer|between:60,250',
            'blood_pressure_diastolic' => 'nullable|integer|between:40,150',
            'heart_rate' => 'nullable|integer|between:30,200',
            'respiratory_rate' => 'nullable|integer|between:8,60',
            'oxygen_saturation' => 'nullable|numeric|between:70,100',
            'weight_value' => 'nullable|numeric|between:1,1000',
            'weight_unit' => 'nullable|in:lbs,kg',
            'height_value' => 'nullable|numeric|between:10,300',
            'height_unit' => 'nullable|in:in,cm',
            'notes' => 'nullable|string',
        ]);

        $validated['encounter_id'] = $encounter->encounter_id;
        $validated['recorded_by'] = auth()->user()->id ?? 1; // Default to 1 if no auth

        VitalSign::create($validated);

        return redirect()
            ->route('encounters.show', $encounter->encounter_id)
            ->with('success', 'Vital signs recorded successfully.');
    }

    /**
     * Show the form for editing vital signs
     */
    public function edit(VitalSign $vitalSign): View
    {
        return view('vital-signs.edit', compact('vitalSign'));
    }

    /**
     * Update vital signs
     */
    public function update(Request $request, VitalSign $vitalSign): RedirectResponse
    {
        $validated = $request->validate([
            'temperature_value' => 'nullable|numeric|between:90,110',
            'temperature_unit' => 'nullable|in:C,F',
            'blood_pressure_systolic' => 'nullable|integer|between:60,250',
            'blood_pressure_diastolic' => 'nullable|integer|between:40,150',
            'heart_rate' => 'nullable|integer|between:30,200',
            'respiratory_rate' => 'nullable|integer|between:8,60',
            'oxygen_saturation' => 'nullable|numeric|between:70,100',
            'weight_value' => 'nullable|numeric|between:1,1000',
            'weight_unit' => 'nullable|in:lbs,kg',
            'height_value' => 'nullable|numeric|between:10,300',
            'height_unit' => 'nullable|in:in,cm',
            'notes' => 'nullable|string',
        ]);

        $vitalSign->update($validated);

        return redirect()
            ->route('encounters.show', $vitalSign->encounter_id)
            ->with('success', 'Vital signs updated successfully.');
    }
}
