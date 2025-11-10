@extends('layouts.app')

@section('title', 'Add Diagnosis')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Add Diagnosis</h1>
        <p class="mt-2 text-sm text-gray-700">
            Patient: <span class="font-medium">{{ $encounter->patient->full_name }}</span> -
            Appointment: {{ $encounter->encounter_date->format('F j, Y \a\t g:i A') }}
        </p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('diagnoses.store', $encounter->encounter_id) }}" class="space-y-6 p-6">
            @csrf

            <!-- Diagnosis Description -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Diagnosis Information</h3>

                <div>
                    <label for="diagnosis_description" class="block text-sm font-medium text-gray-700">Diagnosis Description *</label>
                    <textarea name="diagnosis_description" id="diagnosis_description" rows="3" required
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('diagnosis_description') border-red-300 @enderror"
                              placeholder="Enter the diagnosis description...">{{ old('diagnosis_description') }}</textarea>
                    @error('diagnosis_description')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>
            </div>

            <!-- ICD Codes and Type -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Coding & Classification</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div>
                        <label for="icd10_code" class="block text-sm font-medium text-gray-700">ICD-10 Code</label>
                        <input type="text" name="icd10_code" id="icd10_code"
                               value="{{ old('icd10_code') }}"
                               placeholder="e.g., E11.9"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">International Classification of Diseases, 10th Revision</p>
                    </div>

                    <div>
                        <label for="icd11_code" class="block text-sm font-medium text-gray-700">ICD-11 Code</label>
                        <input type="text" name="icd11_code" id="icd11_code"
                               value="{{ old('icd11_code') }}"
                               placeholder="e.g., 5A14"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">International Classification of Diseases, 11th Revision</p>
                    </div>

                    <div>
                        <label for="diagnosis_type" class="block text-sm font-medium text-gray-700">Diagnosis Type</label>
                        <select name="diagnosis_type" id="diagnosis_type"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <option value="">Select Type</option>
                            <option value="Primary" {{ old('diagnosis_type') == 'Primary' ? 'selected' : '' }}>Primary</option>
                            <option value="Secondary" {{ old('diagnosis_type') == 'Secondary' ? 'selected' : '' }}>Secondary</option>
                            <option value="Differential" {{ old('diagnosis_type') == 'Differential' ? 'selected' : '' }}>Differential</option>
                            <option value="Working" {{ old('diagnosis_type') == 'Working' ? 'selected' : '' }}>Working</option>
                            <option value="Rule Out" {{ old('diagnosis_type') == 'Rule Out' ? 'selected' : '' }}>Rule Out</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Timeline -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Timeline</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div>
                        <label for="onset_date" class="block text-sm font-medium text-gray-700">Onset Date</label>
                        <input type="date" name="onset_date" id="onset_date"
                               value="{{ old('onset_date') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">When symptoms first appeared</p>
                    </div>

                    <div>
                        <label for="resolved_date" class="block text-sm font-medium text-gray-700">Resolved Date</label>
                        <input type="date" name="resolved_date" id="resolved_date"
                               value="{{ old('resolved_date') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">When condition was resolved</p>
                    </div>

                    <div>
                        <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
                        <select name="status" id="status"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <option value="Active" {{ old('status', 'Active') == 'Active' ? 'selected' : '' }}>Active</option>
                            <option value="Resolved" {{ old('status') == 'Resolved' ? 'selected' : '' }}>Resolved</option>
                            <option value="Chronic" {{ old('status') == 'Chronic' ? 'selected' : '' }}>Chronic</option>
                            <option value="Inactive" {{ old('status') == 'Inactive' ? 'selected' : '' }}>Inactive</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Diagnosing Physician -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Diagnosing Physician</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="diagnosed_by" class="block text-sm font-medium text-gray-700">Physician</label>
                        <select name="diagnosed_by" id="diagnosed_by"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <option value="">Select Physician</option>
                            @foreach($providers as $provider)
                                <option value="{{ $provider->provider_id }}"
                                        {{ old('diagnosed_by', $encounter->provider_id) == $provider->provider_id ? 'selected' : '' }}>
                                    {{ $provider->full_name }} - {{ $provider->specialty }}
                                </option>
                            @endforeach
                        </select>
                        <p class="mt-1 text-xs text-gray-500">Defaults to appointment physician</p>
                    </div>
                </div>
            </div>

            <!-- Additional Notes -->
            <div class="pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Notes</h3>

                <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Clinical Notes</label>
                    <textarea name="notes" id="notes" rows="4"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                              placeholder="Additional clinical notes, observations, or context...">{{ old('notes') }}</textarea>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 border-t border-gray-200 pt-6">
                <a href="{{ route('appointments.show', $encounter->encounter_id) }}"
                   class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Cancel
                </a>
                <button type="submit"
                        class="inline-flex justify-center rounded-md border border-transparent bg-medical-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Add Diagnosis
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
