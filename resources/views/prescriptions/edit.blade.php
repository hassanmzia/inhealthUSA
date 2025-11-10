@extends('layouts.app')

@section('title', 'Edit Prescription')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Edit Prescription</h1>
        <p class="mt-2 text-sm text-gray-700">{{ $prescription->medication_name }}</p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('prescriptions.update', $prescription->prescription_id) }}" class="space-y-6 p-6">
            @csrf
            @method('PUT')

            <!-- Medication Information -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Medication Information</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="medication_name" class="block text-sm font-medium text-gray-700">Medication Name *</label>
                        <input type="text" name="medication_name" id="medication_name" required
                               value="{{ old('medication_name', $prescription->medication_name) }}"
                               placeholder="e.g., Amoxicillin"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('medication_name') border-red-300 @enderror">
                        @error('medication_name')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="dosage" class="block text-sm font-medium text-gray-700">Dosage *</label>
                        <input type="text" name="dosage" id="dosage" required
                               value="{{ old('dosage', $prescription->dosage) }}"
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
                            <option value="Once daily" {{ old('frequency', $prescription->frequency) == 'Once daily' ? 'selected' : '' }}>Once daily</option>
                            <option value="Twice daily" {{ old('frequency', $prescription->frequency) == 'Twice daily' ? 'selected' : '' }}>Twice daily</option>
                            <option value="Three times daily" {{ old('frequency', $prescription->frequency) == 'Three times daily' ? 'selected' : '' }}>Three times daily</option>
                            <option value="Four times daily" {{ old('frequency', $prescription->frequency) == 'Four times daily' ? 'selected' : '' }}>Four times daily</option>
                            <option value="Every 4 hours" {{ old('frequency', $prescription->frequency) == 'Every 4 hours' ? 'selected' : '' }}>Every 4 hours</option>
                            <option value="Every 6 hours" {{ old('frequency', $prescription->frequency) == 'Every 6 hours' ? 'selected' : '' }}>Every 6 hours</option>
                            <option value="Every 8 hours" {{ old('frequency', $prescription->frequency) == 'Every 8 hours' ? 'selected' : '' }}>Every 8 hours</option>
                            <option value="Every 12 hours" {{ old('frequency', $prescription->frequency) == 'Every 12 hours' ? 'selected' : '' }}>Every 12 hours</option>
                            <option value="As needed" {{ old('frequency', $prescription->frequency) == 'As needed' ? 'selected' : '' }}>As needed</option>
                            <option value="Weekly" {{ old('frequency', $prescription->frequency) == 'Weekly' ? 'selected' : '' }}>Weekly</option>
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
                            <option value="Oral" {{ old('route', $prescription->route) == 'Oral' ? 'selected' : '' }}>Oral</option>
                            <option value="Topical" {{ old('route', $prescription->route) == 'Topical' ? 'selected' : '' }}>Topical</option>
                            <option value="Intravenous" {{ old('route', $prescription->route) == 'Intravenous' ? 'selected' : '' }}>Intravenous (IV)</option>
                            <option value="Intramuscular" {{ old('route', $prescription->route) == 'Intramuscular' ? 'selected' : '' }}>Intramuscular (IM)</option>
                            <option value="Subcutaneous" {{ old('route', $prescription->route) == 'Subcutaneous' ? 'selected' : '' }}>Subcutaneous</option>
                            <option value="Inhalation" {{ old('route', $prescription->route) == 'Inhalation' ? 'selected' : '' }}>Inhalation</option>
                            <option value="Rectal" {{ old('route', $prescription->route) == 'Rectal' ? 'selected' : '' }}>Rectal</option>
                            <option value="Ophthalmic" {{ old('route', $prescription->route) == 'Ophthalmic' ? 'selected' : '' }}>Ophthalmic</option>
                            <option value="Otic" {{ old('route', $prescription->route) == 'Otic' ? 'selected' : '' }}>Otic</option>
                        </select>
                    </div>

                    <div>
                        <label for="quantity" class="block text-sm font-medium text-gray-700">Quantity</label>
                        <input type="number" name="quantity" id="quantity" min="1"
                               value="{{ old('quantity', $prescription->quantity) }}"
                               placeholder="e.g., 30"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>
            </div>

            <!-- Duration and Refills -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Duration and Refills</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div>
                        <label for="start_date" class="block text-sm font-medium text-gray-700">Start Date</label>
                        <input type="date" name="start_date" id="start_date"
                               value="{{ old('start_date', $prescription->start_date ? $prescription->start_date->format('Y-m-d') : '') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="end_date" class="block text-sm font-medium text-gray-700">End Date</label>
                        <input type="date" name="end_date" id="end_date"
                               value="{{ old('end_date', $prescription->end_date ? $prescription->end_date->format('Y-m-d') : '') }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="refills" class="block text-sm font-medium text-gray-700">Refills Allowed</label>
                        <input type="number" name="refills" id="refills" min="0" max="12"
                               value="{{ old('refills', $prescription->refills) }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 mt-6">
                    <div>
                        <label for="duration" class="block text-sm font-medium text-gray-700">Duration</label>
                        <input type="text" name="duration" id="duration"
                               value="{{ old('duration', $prescription->duration) }}"
                               placeholder="e.g., 10 days, 2 weeks"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>
            </div>

            <!-- Instructions and Notes -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Instructions</h3>

                <div class="grid grid-cols-1 gap-6">
                    <div>
                        <label for="instructions" class="block text-sm font-medium text-gray-700">Patient Instructions</label>
                        <textarea name="instructions" id="instructions" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="e.g., Take with food. Complete full course even if symptoms improve.">{{ old('instructions', $prescription->instructions) }}</textarea>
                    </div>

                    <div>
                        <label for="notes" class="block text-sm font-medium text-gray-700">Pharmacy Notes</label>
                        <textarea name="notes" id="notes" rows="2"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                                  placeholder="Additional notes for the pharmacy...">{{ old('notes', $prescription->notes) }}</textarea>
                    </div>
                </div>
            </div>

            <!-- Status -->
            <div class="border-b border-gray-200 pb-6">
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="status" class="block text-sm font-medium text-gray-700">Status *</label>
                        <select name="status" id="status" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('status') border-red-300 @enderror">
                            <option value="Active" {{ old('status', $prescription->status) == 'Active' ? 'selected' : '' }}>Active</option>
                            <option value="Pending" {{ old('status', $prescription->status) == 'Pending' ? 'selected' : '' }}>Pending</option>
                            <option value="Completed" {{ old('status', $prescription->status) == 'Completed' ? 'selected' : '' }}>Completed</option>
                            <option value="Discontinued" {{ old('status', $prescription->status) == 'Discontinued' ? 'selected' : '' }}>Discontinued</option>
                        </select>
                        @error('status')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 border-t border-gray-200 pt-6">
                <a href="{{ route('prescriptions.show', $prescription->prescription_id) }}"
                   class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Cancel
                </a>
                <button type="submit"
                        class="inline-flex justify-center rounded-md border border-transparent bg-medical-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                    Update Prescription
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
