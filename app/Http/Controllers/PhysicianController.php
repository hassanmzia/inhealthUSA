<?php

namespace App\Http\Controllers;

use App\Models\Provider;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Illuminate\Http\RedirectResponse;

class PhysicianController extends Controller
{
    /**
     * Display a listing of providers
     */
    public function index(Request $request): View
    {
        $query = Provider::with(['encounters' => function($q) {
            $q->orderBy('encounter_date', 'desc')->limit(5);
        }])->active();

        // Search functionality
        if ($request->has('search')) {
            $search = $request->input('search');
            $query->where(function($q) use ($search) {
                $q->where('first_name', 'like', "%{$search}%")
                  ->orWhere('last_name', 'like', "%{$search}%")
                  ->orWhere('specialty', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%")
                  ->orWhere('npi_number', 'like', "%{$search}%");
            });
        }

        // Filter by specialty
        if ($request->has('specialty') && $request->input('specialty') !== '') {
            $query->where('specialty', $request->input('specialty'));
        }

        $providers = $query->orderBy('last_name')->paginate(20);

        // Get unique specialties for filter dropdown
        $specialties = Provider::active()
            ->select('specialty')
            ->distinct()
            ->orderBy('specialty')
            ->pluck('specialty');

        return view('physicians.index', compact('providers', 'specialties'));
    }

    /**
     * Show the form for creating a new provider
     */
    public function create(): View
    {
        return view('physicians.create');
    }

    /**
     * Store a newly created provider
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'first_name' => 'required|string|max:100',
            'last_name' => 'required|string|max:100',
            'specialty' => 'required|string|max:150',
            'license_number' => 'nullable|string|max:50',
            'npi_number' => 'nullable|string|max:10',
            'phone' => 'nullable|string|max:20',
            'email' => 'nullable|email|max:255',
        ]);

        $validated['is_active'] = true;

        $provider = Provider::create($validated);

        return redirect()
            ->route('physicians.show', $provider->provider_id)
            ->with('success', 'Provider created successfully.');
    }

    /**
     * Display the specified provider
     */
    public function show(Provider $provider): View
    {
        $provider->load([
            'encounters' => function($query) {
                $query->with(['patient', 'department'])
                      ->orderBy('encounter_date', 'desc');
            }
        ]);

        // Get provider statistics
        $stats = [
            'total_encounters' => $provider->encounters()->count(),
            'encounters_this_month' => $provider->encounters()
                ->whereMonth('encounter_date', now()->month)
                ->whereYear('encounter_date', now()->year)
                ->count(),
            'active_patients' => $provider->encounters()
                ->distinct('patient_id')
                ->count('patient_id'),
        ];

        return view('physicians.show', compact('provider', 'stats'));
    }

    /**
     * Show the form for editing the specified provider
     */
    public function edit(Provider $provider): View
    {
        return view('physicians.edit', compact('provider'));
    }

    /**
     * Update the specified provider
     */
    public function update(Request $request, Provider $provider): RedirectResponse
    {
        $validated = $request->validate([
            'first_name' => 'required|string|max:100',
            'last_name' => 'required|string|max:100',
            'specialty' => 'required|string|max:150',
            'license_number' => 'nullable|string|max:50',
            'npi_number' => 'nullable|string|max:10',
            'phone' => 'nullable|string|max:20',
            'email' => 'nullable|email|max:255',
        ]);

        $provider->update($validated);

        return redirect()
            ->route('physicians.show', $provider->provider_id)
            ->with('success', 'Provider updated successfully.');
    }

    /**
     * Remove the specified provider (soft delete)
     */
    public function destroy(Provider $provider): RedirectResponse
    {
        $provider->update(['is_active' => false]);

        return redirect()
            ->route('physicians.index')
            ->with('success', 'Provider deactivated successfully.');
    }

    /**
     * Activate a provider
     */
    public function activate(Provider $provider): RedirectResponse
    {
        $provider->update(['is_active' => true]);

        return redirect()
            ->route('physicians.show', $provider->provider_id)
            ->with('success', 'Provider activated successfully.');
    }
}
