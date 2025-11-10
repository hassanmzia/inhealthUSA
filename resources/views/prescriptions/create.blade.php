@extends('layouts.app')

@section('title', 'Create New Prescription')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Create New Prescription</h1>
        <p class="mt-2 text-sm text-gray-700">E-prescribe medication for a patient.</p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('prescriptions.store') }}" class="space-y-6 p-6">
            @csrf

            <!-- Patient and Encounter Selection -->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                    <label for="patient_id" class="block text-sm font-medium text-gray-700">Patient *</label>
                    <select name="patient_id" id="patient_id" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('patient_id') border-red-300 @enderror">
                        <option value="">Select Patient</option>
                        @foreach($patients as $patient)
                            <option value="{{ $patient->patient_id }}" {{ old('patient_id') == $patient->patient_id ? 'selected' : '' }}>
                                {{ $patient->full_name }} - DOB: {{ $patient->date_of_birth->format('Y-m-d') }}
                            </option>
                        @endforeach
                    </select>
                    @error('patient_id')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div>
                    <label for="encounter_id" class="block text-sm font-medium text-gray-700">Encounter</label>
                    <select name="encounter_id" id="encounter_id"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <option value="">Select Encounter (Optional)</option>
                        @foreach($encounters as $encounter)
                            <option value="{{ $encounter->encounter_id }}" {{ old('encounter_id') == $encounter->encounter_id ? 'selected' : '' }}>
                                {{ $encounter->encounter_date->format('Y-m-d') }} - {{ $encounter->encounter_type }}
                            </option>
                        @endforeach
                    </select>
                </div>
            </div>

            <!-- Provider -->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
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

            <!-- Medication Information -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Medication Information</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="medication_name" class="block text-sm font-medium text-gray-700">Medication Name *</label>
                        <input type="text" name="medication_name" id="medication_name" required
                               value="{{ old('medication_name') }}"
                               placeholder="e.g., Amoxicillin"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('medication_name') border-red-300 @enderror">
                        @error('medication_name')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="dosage" class="block text-sm font-medium text-gray-700">Dosage *</label>
                        <input type="text" name="dosage" id="dosage" required
                               value="{{ old('dosage') }}"
                               placeholder="e.g., 500mg"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('dosage') border-red-300 @enderror">
                        @error('dosage')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3 mt-6">
                    <div>
                        <label for="frequency" class="block text-sm font-medium text-gray-700">Frequency *</label>
                        <select name="frequency" id="frequency" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('frequency') border-red-300 @enderror">
                            <option value="">Select Frequency</option>
                            <option value="Once daily" {{ old('frequency') == 'Once daily' ? 'selected' : '' }}>Once daily</option>
                            <option value="Twice daily" {{ old('frequency') == 'Twice daily' ? 'selected' : '' }}>Twice daily</option>
                            <option value="Three times daily" {{ old('frequency') == 'Three times daily' ? 'selected' : '' }}>Three times daily</option>
                            <option value="Four times daily" {{ old('frequency') == 'Four times daily' ? 'selected' : '' }}>Four times daily</option>
                            <option value="Every 4 hours" {{ old('frequency') == 'Every 4 hours' ? 'selected' : '' }}>Every 4 hours</option>
                            <option value="Every 6 hours" {{ old('frequency') == 'Every 6 hours' ? 'selected' : '' }}>Every 6 hours</option>
                            <option value="Every 8 hours" {{ old('frequency') == 'Every 8 hours' ? 'selected' : '' }}>Every 8 hours</option>
                            <option value="Every 12 hours" {{ old('frequency') == 'Every 12 hours' ? 'selected' : '' }}>Every 12 hours</option>
                            <option value="As needed" {{ old('frequency') == 'As needed' ? 'selected' : '' }}>As needed</option>
                            <option value="Weekly" {{ old('frequency') == 'Weekly' ? 'selected' : '' }}>Weekly</option>
                        </select>
                        @error('frequency')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="route" class="block text-sm font-medium text-gray-700">Route</label>
                        <select name="route" id="route"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <option value="">Select Route</option>
                            <option value="Oral" {{ old('route', 'Oral') == 'Oral' ? 'selected' : '' }}>Oral</option>
                            <option value="Topical" {{ old('route') == 'Topical' ? 'selected' : '' }}>Topical</option>
                            <option value="Intravenous" {{ old('route') == 'Intravenous' ? 'selected' : '' }}>Intravenous (IV)</option>
                            <option value="Intramuscular" {{ old('route') == 'Intramuscular' ? 'selected' : '' }}>Intramuscular (IM)</option>
                            <option value="Subcutaneous" {{ old('route') == 'Subcutaneous' ? 'selected' : '' }}>Subcutaneous</option>
                            <option value="Inhalation" {{ old('route') == 'Inhalation' ? 'selected' : '' }}>Inhalation</option>
                            <option value="Rectal" {{ old('route') == 'Rectal' ? 'selected' : '' }}>Rectal</option>
                            <option value="Ophthalmic" {{ old('route') == 'Ophthalmic' ? 'selected' : '' }}>Ophthalmic</option>
                            <option value="Otic" {{ old('route') == 'Otic' ? 'selected' : '' }}>Otic</option>
                        </select>
                    </div>

                    <div>
                        <label for="quantity" class="block text-sm font-medium text-gray-700">Quantity</label>
                        <input type="number" name="quantity" id="quantity" min="1"
                               value="{{ old('quantity') }}"
                               placeholder="e.g., 30"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>
            </div>

            <!-- Duration and Refills -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Duration and Refills</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div>
                        <label for="start_date" class="block text-sm font-medium text-gray-700">Start Date *</label>
                        <input type="date" name="start_date" id="start_date" required
                               value="{{ old('start_date', date('Y-m-d')) }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('start_date') border-red-300 @enderror">
                        @error('start_date')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="end_date" class="block text-sm font-medium text-gray-700">End Date</label>
                        <input type="date" name="end_date" id="end_date"
                               value="{{ old('end_date') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="refills" class="block text-sm font-medium text-gray-700">Refills Allowed</label>
                        <input type="number" name="refills" id="refills" min="0" max="12"
                               value="{{ old('refills', '0') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>
            </div>

            <!-- Instructions and Notes -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Instructions</h3>

                <div class="grid grid-cols-1 gap-6">
                    <div>
                        <label for="instructions" class="block text-sm font-medium text-gray-700">Patient Instructions</label>
                        <textarea name="instructions" id="instructions" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="e.g., Take with food. Complete full course even if symptoms improve.">{{ old('instructions') }}</textarea>
                    </div>

                    <div>
                        <label for="notes" class="block text-sm font-medium text-gray-700">Pharmacy Notes</label>
                        <textarea name="notes" id="notes" rows="2"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Additional notes for the pharmacy...">{{ old('notes') }}</textarea>
                    </div>
                </div>
            </div>

            <!-- Status -->
            <div class="border-t border-gray-200 pt-6">
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="status" class="block text-sm font-medium text-gray-700">Status *</label>
                        <select name="status" id="status" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('status') border-red-300 @enderror">
                            <option value="Active" {{ old('status', 'Active') == 'Active' ? 'selected' : '' }}>Active</option>
                            <option value="Pending" {{ old('status') == 'Pending' ? 'selected' : '' }}>Pending</option>
                            <option value="Completed" {{ old('status') == 'Completed' ? 'selected' : '' }}>Completed</option>
                            <option value="Discontinued" {{ old('status') == 'Discontinued' ? 'selected' : '' }}>Discontinued</option>
                        </select>
                        @error('status')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 border-t border-gray-200 pt-6">
                <a href="{{ route('prescriptions.index') }}"
                   class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Cancel
                </a>
                <button type="submit"
                        class="inline-flex justify-center rounded-md border border-transparent bg-medical-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Create Prescription
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
