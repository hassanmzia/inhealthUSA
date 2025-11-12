<?php

namespace App\Http\Controllers;

use App\Models\Device;
use App\Models\Patient;
use Illuminate\Http\Request;
use Illuminate\View\View;

class DeviceController extends Controller
{
    /**
     * Display devices for a patient
     */
    public function index(Patient $patient): View
    {
        $devices = $patient->devices()->orderBy('created_at', 'desc')->get();

        return view('devices.index', compact('patient', 'devices'));
    }

    /**
     * Show device details
     */
    public function show(Patient $patient, Device $device): View
    {
        // Ensure device belongs to this patient
        if ($device->patient_id !== $patient->patient_id) {
            abort(404);
        }

        return view('devices.show', compact('patient', 'device'));
    }

    /**
     * Show form to create new device
     */
    public function create(Patient $patient): View
    {
        return view('devices.create', compact('patient'));
    }

    /**
     * Store a new device
     */
    public function store(Request $request, Patient $patient)
    {
        $validated = $request->validate([
            'device_unique_id' => 'required|string|max:255|unique:devices,device_unique_id',
            'device_type' => 'required|in:Watch,Ring,EarClip,Adapter,PulseGlucometer',
            'device_name' => 'required|string|max:200',
            'manufacturer' => 'nullable|string|max:200',
            'model_number' => 'nullable|string|max:100',
            'firmware_version' => 'nullable|string|max:50',
            'capabilities' => 'nullable|array',
            'status' => 'required|in:Active,Inactive,Maintenance,Retired',
            'battery_level' => 'nullable|integer|min:0|max:100',
            'registration_date' => 'required|date',
            'notes' => 'nullable|string',
        ]);

        $validated['patient_id'] = $patient->patient_id;

        Device::create($validated);

        return redirect()->route('devices.index', $patient->patient_id)
            ->with('success', 'Device registered successfully.');
    }

    /**
     * Show form to edit device
     */
    public function edit(Patient $patient, Device $device): View
    {
        if ($device->patient_id !== $patient->patient_id) {
            abort(404);
        }

        return view('devices.edit', compact('patient', 'device'));
    }

    /**
     * Update device
     */
    public function update(Request $request, Patient $patient, Device $device)
    {
        if ($device->patient_id !== $patient->patient_id) {
            abort(404);
        }

        $validated = $request->validate([
            'device_unique_id' => 'required|string|max:255|unique:devices,device_unique_id,' . $device->device_id . ',device_id',
            'device_type' => 'required|in:Watch,Ring,EarClip,Adapter,PulseGlucometer',
            'device_name' => 'required|string|max:200',
            'manufacturer' => 'nullable|string|max:200',
            'model_number' => 'nullable|string|max:100',
            'firmware_version' => 'nullable|string|max:50',
            'capabilities' => 'nullable|array',
            'status' => 'required|in:Active,Inactive,Maintenance,Retired',
            'battery_level' => 'nullable|integer|min:0|max:100',
            'registration_date' => 'required|date',
            'notes' => 'nullable|string',
        ]);

        $device->update($validated);

        return redirect()->route('devices.show', [$patient->patient_id, $device->device_id])
            ->with('success', 'Device updated successfully.');
    }

    /**
     * Delete device
     */
    public function destroy(Patient $patient, Device $device)
    {
        if ($device->patient_id !== $patient->patient_id) {
            abort(404);
        }

        $device->delete();

        return redirect()->route('devices.index', $patient->patient_id)
            ->with('success', 'Device removed successfully.');
    }
}
