<?php

namespace App\Http\Controllers;

use App\Models\TreatmentPlan;
use App\Models\Encounter;
use App\Models\Provider;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\View\View;

class TreatmentPlanController extends Controller
{
    /**
     * Display a listing of treatment plans
     */
    public function index(): View
    {
        $treatmentPlans = TreatmentPlan::with(['encounter.patient', 'creator'])
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return view('treatment-plans.index', compact('treatmentPlans'));
    }

    /**
     * Show a specific treatment plan
     */
    public function show(TreatmentPlan $treatmentPlan): View
    {
        $treatmentPlan->load(['encounter.patient', 'encounter.provider', 'creator']);

        return view('treatment-plans.show', compact('treatmentPlan'));
    }

    /**
     * Show the form for creating a new treatment plan
     */
    public function create(Encounter $encounter): View
    {
        $providers = Provider::active()->orderBy('last_name')->orderBy('first_name')->get();
        return view('treatment-plans.create', compact('encounter', 'providers'));
    }

    /**
     * Store a newly created treatment plan
     */
    public function store(Request $request, Encounter $encounter): RedirectResponse
    {
        $validated = $request->validate([
            'plan_description' => 'required|string',
            'diagnostic_workup' => 'nullable|string',
            'treatment_details' => 'nullable|string',
            'patient_education' => 'nullable|string',
            'follow_up_instructions' => 'nullable|string',
            'prevention_measures' => 'nullable|string',
            'clingpt_suggestions' => 'nullable|string',
        ]);

        $validated['encounter_id'] = $encounter->encounter_id;
        $validated['created_by'] = auth()->user()->id ?? 1; // Default to 1 if no auth

        $treatmentPlan = TreatmentPlan::create($validated);

        return redirect()
            ->route('treatment-plans.show', $treatmentPlan->plan_id)
            ->with('success', 'Treatment plan created successfully.');
    }

    /**
     * Show the form for editing a treatment plan
     */
    public function edit(TreatmentPlan $treatmentPlan): View
    {
        $providers = Provider::active()->orderBy('last_name')->orderBy('first_name')->get();
        $encounter = $treatmentPlan->encounter;

        return view('treatment-plans.edit', compact('treatmentPlan', 'providers', 'encounter'));
    }

    /**
     * Update a treatment plan
     */
    public function update(Request $request, TreatmentPlan $treatmentPlan): RedirectResponse
    {
        $validated = $request->validate([
            'plan_description' => 'required|string',
            'diagnostic_workup' => 'nullable|string',
            'treatment_details' => 'nullable|string',
            'patient_education' => 'nullable|string',
            'follow_up_instructions' => 'nullable|string',
            'prevention_measures' => 'nullable|string',
            'clingpt_suggestions' => 'nullable|string',
        ]);

        $treatmentPlan->update($validated);

        return redirect()
            ->route('treatment-plans.show', $treatmentPlan->plan_id)
            ->with('success', 'Treatment plan updated successfully.');
    }

    /**
     * Remove a treatment plan
     */
    public function destroy(TreatmentPlan $treatmentPlan): RedirectResponse
    {
        $treatmentPlan->delete();

        return redirect()
            ->route('treatment-plans.index')
            ->with('success', 'Treatment plan deleted successfully.');
    }
}
