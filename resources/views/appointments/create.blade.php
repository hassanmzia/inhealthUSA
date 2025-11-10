@extends('layouts.app')

@section('title', 'Create New Encounter')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Create New Encounter</h1>
        <p class="mt-2 text-sm text-gray-700">Schedule a new patient visit or appointment.</p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('appointments.store') }}" class="space-y-6 p-6">
            @csrf

            <!-- Patient Selection ---->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                    <label for="patient_id" class="block text-sm font-medium text-gray-700">Patient *</label>
                    <select name="patient_id" id="patient_id" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('patient_id') border-red-300 @enderror">
                        <option value="">Select Patient</option>
                        @foreach($patients as $patient)
                            <option value="{{ $patient->patient_id }}" {{ old('patient_id') == $patient->patient_id ? 'selected' : '' }}>
                                {{ $patient->full_name }} - {{ $patient->date_of_birth->format('Y-m-d') }}
                            </option>
                        @endforeach
                    </select>
                    @error('patient_id')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div>
                    <label for="provider_id" class="block text-sm font-medium text-gray-700">Provider *</label>
                    <select name="provider_id" id="provider_id" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('provider_id') border-red-300 @enderror">
                        <option value="">Select Provider</option>
                        @foreach($providers as $provider)
                            <option value="{{ $provider->provider_id }}" {{ old('provider_id') == $provider->provider_id ? 'selected' : '' }}>
                                {{ $provider->full_name }} - {{ $provider->specialty }}
                            </option>
                        @endforeach
                    </select>
                    @error('provider_id')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>
            </div>

            <!-- Date/Time and Type ---->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                <div>
                    <label for="encounter_date" class="block text-sm font-medium text-gray-700">Encounter Date/Time *</label>
                    <input type="datetime-local" name="encounter_date" id="encounter_date" required
                           value="{{ old('encounter_date') }}"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('encounter_date') border-red-300 @enderror">
                    @error('encounter_date')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div>
                    <label for="encounter_type" class="block text-sm font-medium text-gray-700">Encounter Type *</label>
                    <select name="encounter_type" id="encounter_type" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('encounter_type') border-red-300 @enderror">
                        <option value="">Select Type</option>
                        <option value="Office Visit" {{ old('encounter_type') == 'Office Visit' ? 'selected' : '' }}>Office Visit</option>
                        <option value="Emergency" {{ old('encounter_type') == 'Emergency' ? 'selected' : '' }}>Emergency</option>
                        <option value="Inpatient" {{ old('encounter_type') == 'Inpatient' ? 'selected' : '' }}>Inpatient</option>
                        <option value="Outpatient" {{ old('encounter_type') == 'Outpatient' ? 'selected' : '' }}>Outpatient</option>
                        <option value="Telehealth" {{ old('encounter_type') == 'Telehealth' ? 'selected' : '' }}>Telehealth</option>
                        <option value="Follow-up" {{ old('encounter_type') == 'Follow-up' ? 'selected' : '' }}>Follow-up</option>
                    </select>
                    @error('encounter_type')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div>
                    <label for="department_id" class="block text-sm font-medium text-gray-700">Department</label>
                    <select name="department_id" id="department_id"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <option value="">Select Department</option>
                        @foreach($departments as $department)
                            <option value="{{ $department->department_id }}" {{ old('department_id') == $department->department_id ? 'selected' : '' }}>
                                {{ $department->department_name }}
                            </option>
                        @endforeach
                    </select>
                </div>
            </div>

            <!-- Status ---->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                    <label for="status" class="block text-sm font-medium text-gray-700">Status *</label>
                    <select name="status" id="status" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('status') border-red-300 @enderror">
                        <option value="Scheduled" {{ old('status', 'Scheduled') == 'Scheduled' ? 'selected' : '' }}>Scheduled</option>
                        <option value="In Progress" {{ old('status') == 'In Progress' ? 'selected' : '' }}>In Progress</option>
                        <option value="Completed" {{ old('status') == 'Completed' ? 'selected' : '' }}>Completed</option>
                        <option value="Cancelled" {{ old('status') == 'Cancelled' ? 'selected' : '' }}>Cancelled</option>
                    </select>
                    @error('status')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>
            </div>

            <!-- Chief Complaint ---->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Chief Complaint</h3>

                <div>
                    <label for="chief_complaint" class="block text-sm font-medium text-gray-700">Reason for Visit</label>
                    <textarea name="chief_complaint" id="chief_complaint" rows="4"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                              placeholder="Describe the reason for this encounter...">{{ old('chief_complaint') }}</textarea>
                </div>
            </div>

            <!-- Notes ---->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Notes</h3>

                <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                    <textarea name="notes" id="notes" rows="4"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                              placeholder="Any additional notes or instructions...">{{ old('notes') }}</textarea>
                </div>
            </div>

            <!-- Actions ---->
            <div class="flex justify-end space-x-3 border-t border-gray-200 pt-6">
                <a href="{{ route('appointments.index') }}"
                   class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Cancel
                </a>
                <button type="submit"
                        class="inline-flex justify-center rounded-md border border-transparent bg-medical-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Create Encounter
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
