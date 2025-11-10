@extends('layouts.app')

@section('title', 'Encounter Details')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="mb-8 sm:flex sm:items-center sm:justify-between">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Encounter Details</h1>
            <p class="mt-2 text-sm text-gray-700">
                {{ optional($encounter->encounter_date)->format('F j, Y \a\t g:i A') ?? 'N/A' }} - {{ $encounter->encounter_type }}
            </p>
        </div>
        <div class="mt-4 sm:mt-0 flex space-x-3">
            @if($encounter->status !== 'Completed')
                <form method="POST" action="{{ route('appointments.complete', $encounter->encounter_id) }}">
                    @csrf
                    <button type="submit"
                            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700">
                        Complete Encounter
                    </button>
                </form>
            @endif
            <a href="{{ route('appointments.edit', $encounter->encounter_id) }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Edit
            </a>
            <a href="{{ route('appointments.index') }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Back to List
            </a>
        </div>
    </div>

    <!-- Encounter Overview -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Encounter Information</h3>
        </div>
        <div class="border-t border-gray-200">
            <dl>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Patient</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <a href="{{ route('patients.show', $encounter->patient->patient_id) }}"
                           class="text-medical-blue hover:underline">
                            {{ $encounter->patient->full_name }}
                        </a>
                        <span class="text-gray-500 ml-2">
                            (DOB: {{ optional($encounter->patient->date_of_birth)->format('Y-m-d') ?? 'N/A' }})
                        </span>
                    </dd>
                </div>
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Provider</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <a href="{{ route('physicians.show', $encounter->provider->provider_id) }}"
                           class="text-medical-blue hover:underline">
                            {{ $encounter->provider->full_name }}
                        </a>
                        <span class="text-gray-500 ml-2">{{ $encounter->provider->specialty }}</span>
                    </dd>
                </div>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Department</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ $encounter->department->department_name ?? 'Not specified' }}
                    </dd>
                </div>
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Encounter Type</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $encounter->encounter_type }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Status</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            @if($encounter->status === 'Completed') bg-green-100 text-green-800
                            @elseif($encounter->status === 'In Progress') bg-yellow-100 text-yellow-800
                            @elseif($encounter->status === 'Scheduled') bg-blue-100 text-blue-800
                            @else bg-gray-100 text-gray-800
                            @endif">
                            {{ $encounter->status }}
                        </span>
                    </dd>
                </div>
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Date & Time</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ optional($encounter->encounter_date)->format('F j, Y \a\t g:i A') ?? 'N/A' }}
                    </dd>
                </div>
            </dl>
        </div>
    </div>

    <!-- Chief Complaints -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Chief Complaints</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            @forelse($encounter->chiefComplaints as $complaint)
                <div class="mb-4 last:mb-0">
                    <h4 class="text-sm font-medium text-gray-900">{{ $complaint->complaint_text }}</h4>
                    @if($complaint->onset_date)
                        <p class="text-sm text-gray-500 mt-1">Onset: {{ optional($complaint->onset_date)->format('Y-m-d') ?? 'N/A' }}</p>
                    @endif
                    @if($complaint->severity)
                        <p class="text-sm text-gray-500">Severity: {{ $complaint->severity }}/10</p>
                    @endif
                    @if($complaint->description)
                        <p class="text-sm text-gray-700 mt-2">{{ $complaint->description }}</p>
                    @endif
                </div>
            @empty
                <p class="text-sm text-gray-500">No chief complaints recorded.</p>
            @endforelse
        </div>
    </div>

    <!-- Vital Signs -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Vital Signs</h3>
            <a href="{{ route('vital-signs.create', $encounter->encounter_id) }}"
               class="text-sm text-medical-blue hover:underline">
                Add Vital Signs
            </a>
        </div>
        @if($encounter->vitalSigns->count() > 0)
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">BP</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">HR</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Temp</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RR</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">O2 Sat</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        @foreach($encounter->vitalSigns as $vital)
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ optional($vital->recorded_at)->format('g:i A') ?? 'N/A' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                @if($vital->blood_pressure_systolic && $vital->blood_pressure_diastolic)
                                    {{ $vital->blood_pressure_systolic }}/{{ $vital->blood_pressure_diastolic }} mmHg
                                @else
                                    N/A
                                @endif
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ $vital->heart_rate ?? 'N/A' }} @if($vital->heart_rate)bpm@endif
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                @if($vital->temperature_value)
                                    {{ $vital->temperature_value }}°{{ $vital->temperature_unit ?? 'F' }}
                                @else
                                    N/A
                                @endif
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ $vital->respiratory_rate ?? 'N/A' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ $vital->oxygen_saturation ?? 'N/A' }}%
                            </td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @else
            <div class="px-4 py-5 sm:px-6">
                <p class="text-sm text-gray-500">No vital signs recorded.</p>
            </div>
        @endif
    </div>

    <!-- Physical Examination -->
    @if($encounter->physicalExamination)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Physical Examination</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            <div class="prose max-w-none text-sm text-gray-700">
                {{ $encounter->physicalExamination->examination_findings }}
            </div>
        </div>
    </div>
    @endif

    <!-- Diagnoses -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Diagnoses</h3>
            <a href="{{ route('diagnoses.create', $encounter->encounter_id) }}"
               class="text-sm text-medical-blue hover:underline">
                Add Diagnosis
            </a>
        </div>
        @if($encounter->diagnoses->count() > 0)
            <ul class="divide-y divide-gray-200">
                @foreach($encounter->diagnoses as $diagnosis)
                <li class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p class="text-sm font-medium text-gray-900">{{ $diagnosis->diagnosis_description }}</p>
                            @if($diagnosis->icd_code)
                                <p class="text-sm text-gray-500">ICD Code: {{ $diagnosis->icd_code }}</p>
                            @endif
                            @if($diagnosis->type)
                                <span class="mt-1 inline-flex px-2 text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                    {{ $diagnosis->type }}
                                </span>
                            @endif
                        </div>
                        <a href="{{ route('diagnoses.edit', $diagnosis->diagnosis_id) }}"
                           class="text-sm text-medical-blue hover:underline">
                            Edit
                        </a>
                    </div>
                </li>
                @endforeach
            </ul>
        @else
            <div class="px-4 py-5 sm:px-6">
                <p class="text-sm text-gray-500">No diagnoses recorded.</p>
            </div>
        @endif
    </div>

    <!-- Clinical Impression -->
    @if($encounter->clinicalImpression)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Clinical Impression</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            <div class="prose max-w-none text-sm text-gray-700">
                {{ $encounter->clinicalImpression->impression_text }}
            </div>
        </div>
    </div>
    @endif

    <!-- Treatment Plan -->
    @if($encounter->treatmentPlan)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Treatment Plan</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            <div class="prose max-w-none text-sm text-gray-700">
                {{ $encounter->treatmentPlan->plan_description }}
            </div>
            @if($encounter->treatmentPlan->follow_up_date)
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <p class="text-sm text-gray-700">
                        <span class="font-medium">Follow-up Date:</span>
                        {{ optional($encounter->treatmentPlan->follow_up_date)->format('F j, Y') ?? 'N/A' }}
                    </p>
                </div>
            @endif
        </div>
    </div>
    @endif

    <!-- Prescriptions -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Prescriptions</h3>
            <a href="{{ route('prescriptions.create') }}?encounter_id={{ $encounter->encounter_id }}"
               class="text-sm text-medical-blue hover:underline">
                Add Prescription
            </a>
        </div>
        @if($encounter->prescriptions->count() > 0)
            <ul class="divide-y divide-gray-200">
                @foreach($encounter->prescriptions as $prescription)
                <li class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p class="text-sm font-medium text-gray-900">{{ $prescription->medication_name }}</p>
                            <p class="text-sm text-gray-500">
                                {{ $prescription->dosage }} - {{ $prescription->frequency }}
                            </p>
                            @if($prescription->instructions)
                                <p class="text-sm text-gray-600 mt-1">{{ $prescription->instructions }}</p>
                            @endif
                            <span class="mt-1 inline-flex px-2 text-xs leading-5 font-semibold rounded-full
                                @if($prescription->status === 'Active') bg-green-100 text-green-800
                                @elseif($prescription->status === 'Discontinued') bg-red-100 text-red-800
                                @else bg-gray-100 text-gray-800
                                @endif">
                                {{ $prescription->status }}
                            </span>
                        </div>
                        <a href="{{ route('prescriptions.show', $prescription->prescription_id) }}"
                           class="text-sm text-medical-blue hover:underline">
                            View
                        </a>
                    </div>
                </li>
                @endforeach
            </ul>
        @else
            <div class="px-4 py-5 sm:px-6">
                <p class="text-sm text-gray-500">No prescriptions recorded.</p>
            </div>
        @endif
    </div>
</div>
@endsection
