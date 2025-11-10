@extends('layouts.app')

@section('title', 'Record Vital Signs')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Record Vital Signs</h1>
        <p class="mt-2 text-sm text-gray-700">
            Patient: <span class="font-medium">{{ $encounter->patient->full_name }}</span> -
            Appointment: {{ $encounter->encounter_date->format('F j, Y \a\t g:i A') }}
        </p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('vital-signs.store', $encounter->encounter_id) }}" class="space-y-6 p-6">
            @csrf

            <!-- Blood Pressure -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Blood Pressure</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="blood_pressure_systolic" class="block text-sm font-medium text-gray-700">Systolic (mmHg)</label>
                        <input type="number" name="blood_pressure_systolic" id="blood_pressure_systolic"
                               value="{{ old('blood_pressure_systolic') }}"
                               min="0" max="300" step="1"
                               placeholder="120"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('blood_pressure_systolic') border-red-300 @enderror">
                        @error('blood_pressure_systolic')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="blood_pressure_diastolic" class="block text-sm font-medium text-gray-700">Diastolic (mmHg)</label>
                        <input type="number" name="blood_pressure_diastolic" id="blood_pressure_diastolic"
                               value="{{ old('blood_pressure_diastolic') }}"
                               min="0" max="200" step="1"
                               placeholder="80"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('blood_pressure_diastolic') border-red-300 @enderror">
                        @error('blood_pressure_diastolic')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Heart Rate and Temperature -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Heart Rate & Temperature</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="heart_rate" class="block text-sm font-medium text-gray-700">Heart Rate (bpm)</label>
                        <input type="number" name="heart_rate" id="heart_rate"
                               value="{{ old('heart_rate') }}"
                               min="0" max="300" step="1"
                               placeholder="72"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('heart_rate') border-red-300 @enderror">
                        @error('heart_rate')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="temperature_value" class="block text-sm font-medium text-gray-700">Temperature</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <input type="number" name="temperature_value" id="temperature_value"
                                   value="{{ old('temperature_value') }}"
                                   min="0" max="120" step="0.1"
                                   placeholder="98.6"
                                   class="flex-1 rounded-none rounded-l-md border-gray-300 focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('temperature_value') border-red-300 @enderror">
                            <select name="temperature_unit"
                                    class="inline-flex items-center rounded-r-md border border-l-0 border-gray-300 bg-gray-50 px-3 text-sm text-gray-900">
                                <option value="F" {{ old('temperature_unit', 'F') == 'F' ? 'selected' : '' }}>°F</option>
                                <option value="C" {{ old('temperature_unit') == 'C' ? 'selected' : '' }}>°C</option>
                            </select>
                        </div>
                        @error('temperature_value')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Respiratory Rate and Oxygen Saturation -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Respiratory & Oxygen</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="respiratory_rate" class="block text-sm font-medium text-gray-700">Respiratory Rate (breaths/min)</label>
                        <input type="number" name="respiratory_rate" id="respiratory_rate"
                               value="{{ old('respiratory_rate') }}"
                               min="0" max="100" step="1"
                               placeholder="16"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="oxygen_saturation" class="block text-sm font-medium text-gray-700">Oxygen Saturation (%)</label>
                        <input type="number" name="oxygen_saturation" id="oxygen_saturation"
                               value="{{ old('oxygen_saturation') }}"
                               min="0" max="100" step="0.1"
                               placeholder="98"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>
                </div>
            </div>

            <!-- Weight and Height -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Weight & Height</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="weight_value" class="block text-sm font-medium text-gray-700">Weight</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <input type="number" name="weight_value" id="weight_value"
                                   value="{{ old('weight_value') }}"
                                   min="0" max="1000" step="0.1"
                                   placeholder="150"
                                   class="flex-1 rounded-none rounded-l-md border-gray-300 focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <select name="weight_unit"
                                    class="inline-flex items-center rounded-r-md border border-l-0 border-gray-300 bg-gray-50 px-3 text-sm text-gray-900">
                                <option value="lbs" {{ old('weight_unit', 'lbs') == 'lbs' ? 'selected' : '' }}>lbs</option>
                                <option value="kg" {{ old('weight_unit') == 'kg' ? 'selected' : '' }}>kg</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label for="height_value" class="block text-sm font-medium text-gray-700">Height</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <input type="number" name="height_value" id="height_value"
                                   value="{{ old('height_value') }}"
                                   min="0" max="300" step="0.1"
                                   placeholder="68"
                                   class="flex-1 rounded-none rounded-l-md border-gray-300 focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                            <select name="height_unit"
                                    class="inline-flex items-center rounded-r-md border border-l-0 border-gray-300 bg-gray-50 px-3 text-sm text-gray-900">
                                <option value="in" {{ old('height_unit', 'in') == 'in' ? 'selected' : '' }}>inches</option>
                                <option value="cm" {{ old('height_unit') == 'cm' ? 'selected' : '' }}>cm</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- BMI -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Body Mass Index</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="bmi" class="block text-sm font-medium text-gray-700">BMI</label>
                        <input type="number" name="bmi" id="bmi"
                               value="{{ old('bmi') }}"
                               min="0" max="100" step="0.1"
                               placeholder="25.0"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">Leave blank to auto-calculate from weight and height</p>
                    </div>
                </div>
            </div>

            <!-- Notes -->
            <div class="pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Notes</h3>

                <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                    <textarea name="notes" id="notes" rows="3"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm"
                              placeholder="Any additional observations or notes...">{{ old('notes') }}</textarea>
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
                    Record Vital Signs
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
