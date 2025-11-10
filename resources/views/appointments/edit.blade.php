@extends('layouts.app')

@section('title', 'Edit Appointment')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Edit Appointment</h1>
        <p class="mt-2 text-sm text-gray-700">
            Patient: <span class="font-medium">{{ $encounter->patient->full_name }}</span>
        </p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('appointments.update', $encounter->encounter_id) }}" class="space-y-6 p-6">
            @csrf
            @method('PUT')

            <!-- Patient Information (Read-only) -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Patient Information</h3>

                <div class="bg-gray-50 rounded-md p-4">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div>
                            <span class="text-sm font-medium text-gray-500">Name:</span>
                            <p class="mt-1 text-sm text-gray-900">{{ $encounter->patient->full_name }}</p>
                        </div>
                        <div>
                            <span class="text-sm font-medium text-gray-500">Date of Birth:</span>
                            <p class="mt-1 text-sm text-gray-900">{{ $encounter->patient->date_of_birth->format('Y-m-d') }}</p>
                        </div>
                        <div>
                            <span class="text-sm font-medium text-gray-500">MRN:</span>
                            <p class="mt-1 text-sm text-gray-900">{{ $encounter->patient->patient_id }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Appointment Details -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Appointment Details</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="provider_id" class="block text-sm font-medium text-gray-700">Physician *</label>
                        <select name="provider_id" id="provider_id" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('provider_id') border-red-300 @enderror">
                            <option value="">Select Physician</option>
                            @foreach($providers as $provider)
                                <option value="{{ $provider->provider_id }}"
                                        {{ old('provider_id', $encounter->provider_id) == $provider->provider_id ? 'selected' : '' }}>
                                    {{ $provider->full_name }} - {{ $provider->specialty }}
                                </option>
                            @endforeach
                        </select>
                        @error('provider_id')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="department_id" class="block text-sm font-medium text-gray-700">Department</label>
                        <select name="department_id" id="department_id"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <option value="">Select Department</option>
                            @foreach($departments as $department)
                                <option value="{{ $department->department_id }}"
                                        {{ old('department_id', $encounter->department_id) == $department->department_id ? 'selected' : '' }}>
                                    {{ $department->department_name }}
                                </option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 mt-6">
                    <div>
                        <label for="encounter_date" class="block text-sm font-medium text-gray-700">Appointment Date & Time *</label>
                        <input type="datetime-local" name="encounter_date" id="encounter_date" required
                               value="{{ old('encounter_date', $encounter->encounter_date ? $encounter->encounter_date->format('Y-m-d\TH:i') : '') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('encounter_date') border-red-300 @enderror">
                        @error('encounter_date')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="encounter_type" class="block text-sm font-medium text-gray-700">Appointment Type *</label>
                        <select name="encounter_type" id="encounter_type" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('encounter_type') border-red-300 @enderror">
                            <option value="">Select Type</option>
                            <option value="Office Visit" {{ old('encounter_type', $encounter->encounter_type) == 'Office Visit' ? 'selected' : '' }}>Office Visit</option>
                            <option value="Follow-up" {{ old('encounter_type', $encounter->encounter_type) == 'Follow-up' ? 'selected' : '' }}>Follow-up</option>
                            <option value="Annual Physical" {{ old('encounter_type', $encounter->encounter_type) == 'Annual Physical' ? 'selected' : '' }}>Annual Physical</option>
                            <option value="Urgent Care" {{ old('encounter_type', $encounter->encounter_type) == 'Urgent Care' ? 'selected' : '' }}>Urgent Care</option>
                            <option value="Consultation" {{ old('encounter_type', $encounter->encounter_type) == 'Consultation' ? 'selected' : '' }}>Consultation</option>
                            <option value="Telemedicine" {{ old('encounter_type', $encounter->encounter_type) == 'Telemedicine' ? 'selected' : '' }}>Telemedicine</option>
                            <option value="Emergency" {{ old('encounter_type', $encounter->encounter_type) == 'Emergency' ? 'selected' : '' }}>Emergency</option>
                            <option value="Procedure" {{ old('encounter_type', $encounter->encounter_type) == 'Procedure' ? 'selected' : '' }}>Procedure</option>
                            <option value="Lab Review" {{ old('encounter_type', $encounter->encounter_type) == 'Lab Review' ? 'selected' : '' }}>Lab Review</option>
                        </select>
                        @error('encounter_type')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 mt-6">
                    <div>
                        <label for="status" class="block text-sm font-medium text-gray-700">Status *</label>
                        <select name="status" id="status" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('status') border-red-300 @enderror">
                            <option value="Scheduled" {{ old('status', $encounter->status) == 'Scheduled' ? 'selected' : '' }}>Scheduled</option>
                            <option value="Checked In" {{ old('status', $encounter->status) == 'Checked In' ? 'selected' : '' }}>Checked In</option>
                            <option value="In Progress" {{ old('status', $encounter->status) == 'In Progress' ? 'selected' : '' }}>In Progress</option>
                            <option value="Completed" {{ old('status', $encounter->status) == 'Completed' ? 'selected' : '' }}>Completed</option>
                            <option value="Cancelled" {{ old('status', $encounter->status) == 'Cancelled' ? 'selected' : '' }}>Cancelled</option>
                            <option value="No Show" {{ old('status', $encounter->status) == 'No Show' ? 'selected' : '' }}>No Show</option>
                        </select>
                        @error('status')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Clinical Information -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Clinical Information</h3>

                <div class="grid grid-cols-1 gap-6">
                    <div>
                        <label for="chief_complaint" class="block text-sm font-medium text-gray-700">Chief Complaint</label>
                        <textarea name="chief_complaint" id="chief_complaint" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Primary reason for visit...">{{ old('chief_complaint', $encounter->chief_complaint) }}</textarea>
                    </div>

                    <div>
                        <label for="clinical_impression" class="block text-sm font-medium text-gray-700">Clinical Impression</label>
                        <textarea name="clinical_impression" id="clinical_impression" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Clinical assessment and findings...">{{ old('clinical_impression', $encounter->clinical_impression) }}</textarea>
                    </div>

                    <div>
                        <label for="treatment_plan" class="block text-sm font-medium text-gray-700">Treatment Plan</label>
                        <textarea name="treatment_plan" id="treatment_plan" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Recommended treatments and follow-up...">{{ old('treatment_plan', $encounter->treatment_plan) }}</textarea>
                    </div>

                    <div>
                        <label for="notes" class="block text-sm font-medium text-gray-700">Additional Notes</label>
                        <textarea name="notes" id="notes" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Any additional notes or observations...">{{ old('notes', $encounter->notes) }}</textarea>
                    </div>
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
                    Update Appointment
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
