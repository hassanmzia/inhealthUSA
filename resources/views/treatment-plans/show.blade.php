@extends('layouts.app')

@section('title', 'Treatment Plan Details')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <div class="flex justify-between items-start">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">Treatment Plan</h1>
                <p class="mt-2 text-sm text-gray-700">
                    Patient: <a href="{{ route('patients.show', $treatmentPlan->encounter->patient->patient_id) }}"
                               class="font-medium text-medical-blue hover:underline">{{ $treatmentPlan->encounter->patient->full_name }}</a>
                </p>
                <p class="mt-1 text-sm text-gray-700">
                    Encounter: {{ $treatmentPlan->encounter->encounter_date->format('F j, Y \a\t g:i A') }}
                </p>
            </div>
            <div class="flex space-x-3">
                <a href="{{ route('treatment-plans.edit', $treatmentPlan->plan_id) }}"
                   class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                    Edit
                </a>
                <a href="{{ route('treatment-plans.index') }}"
                   class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                    Back to List
                </a>
            </div>
        </div>
    </div>

    @if(session('success'))
    <div class="mb-4 rounded-md bg-green-50 p-4">
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium text-green-800">{{ session('success') }}</p>
            </div>
        </div>
    </div>
    @endif

    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Plan Information</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Created {{ $treatmentPlan->created_at->format('F j, Y \a\t g:i A') }} by {{ $treatmentPlan->creator->full_name ?? 'N/A' }}</p>
        </div>

        <div class="px-4 py-5 sm:p-6">
            <!-- Plan Description -->
            <div class="mb-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Plan Description</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->plan_description }}</div>
            </div>

            <!-- Diagnostic Workup -->
            @if($treatmentPlan->diagnostic_workup)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Diagnostic Workup</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->diagnostic_workup }}</div>
            </div>
            @endif

            <!-- Treatment Details -->
            @if($treatmentPlan->treatment_details)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Treatment Details</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->treatment_details }}</div>
            </div>
            @endif

            <!-- Patient Education -->
            @if($treatmentPlan->patient_education)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Patient Education</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->patient_education }}</div>
            </div>
            @endif

            <!-- Follow-up Instructions -->
            @if($treatmentPlan->follow_up_instructions)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Follow-up Instructions</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->follow_up_instructions }}</div>
            </div>
            @endif

            <!-- Prevention Measures -->
            @if($treatmentPlan->prevention_measures)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Prevention Measures</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line">{{ $treatmentPlan->prevention_measures }}</div>
            </div>
            @endif

            <!-- AI Suggestions -->
            @if($treatmentPlan->clingpt_suggestions)
            <div class="mb-6 border-t border-gray-200 pt-6">
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">ClinGPT AI Suggestions</h4>
                <div class="text-sm text-gray-900 whitespace-pre-line bg-blue-50 p-4 rounded-md">{{ $treatmentPlan->clingpt_suggestions }}</div>
            </div>
            @endif
        </div>

        <!-- Related Information -->
        <div class="bg-gray-50 px-4 py-5 sm:px-6">
            <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Related Information</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <span class="text-sm font-medium text-gray-700">Patient:</span>
                    <a href="{{ route('patients.show', $treatmentPlan->encounter->patient->patient_id) }}"
                       class="ml-2 text-sm text-medical-blue hover:underline">
                        {{ $treatmentPlan->encounter->patient->full_name }}
                    </a>
                </div>
                <div>
                    <span class="text-sm font-medium text-gray-700">Encounter:</span>
                    <a href="{{ route('appointments.show', $treatmentPlan->encounter->encounter_id) }}"
                       class="ml-2 text-sm text-medical-blue hover:underline">
                        View Encounter
                    </a>
                </div>
                <div>
                    <span class="text-sm font-medium text-gray-700">Provider:</span>
                    <span class="ml-2 text-sm text-gray-900">{{ $treatmentPlan->encounter->provider->full_name ?? 'N/A' }}</span>
                </div>
                <div>
                    <span class="text-sm font-medium text-gray-700">Created By:</span>
                    <span class="ml-2 text-sm text-gray-900">{{ $treatmentPlan->creator->full_name ?? 'N/A' }}</span>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
