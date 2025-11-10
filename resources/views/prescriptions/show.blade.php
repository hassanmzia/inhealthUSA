@extends('layouts.app')

@section('title', 'Prescription Details')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="mb-8 sm:flex sm:items-center sm:justify-between">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Prescription Details</h1>
            <p class="mt-2 text-sm text-gray-700">{{ $prescription->medication_name }}</p>
        </div>
        <div class="mt-4 sm:mt-0 flex space-x-3">
            @if($prescription->status !== 'Discontinued')
                <form method="POST" action="{{ route('prescriptions.discontinue', $prescription->prescription_id) }}">
                    @csrf
                    <button type="submit"
                            onclick="return confirm('Are you sure you want to discontinue this prescription?')"
                            class="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50">
                        Discontinue
                    </button>
                </form>
            @endif
            <a href="{{ route('prescriptions.edit', $prescription->prescription_id) }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Edit
            </a>
            <a href="{{ route('prescriptions.index') }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Back to List
            </a>
        </div>
    </div>

    <!-- Status Badge -->
    <div class="mb-8">
        <span class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full
            @if($prescription->status === 'Active') bg-green-100 text-green-800
            @elseif($prescription->status === 'Pending') bg-yellow-100 text-yellow-800
            @elseif($prescription->status === 'Discontinued') bg-red-100 text-red-800
            @elseif($prescription->status === 'Completed') bg-gray-100 text-gray-800
            @else bg-blue-100 text-blue-800
            @endif">
            {{ $prescription->status }}
        </span>
    </div>

    <!-- Patient and Physician Information -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Patient & Physician Information</h3>
        </div>
        <div class="border-t border-gray-200">
            <dl>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Patient</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <a href="{{ route('patients.show', $prescription->patient->patient_id) }}"
                           class="text-medical-blue hover:underline">
                            {{ $prescription->patient->full_name }}
                        </a>
                        <span class="text-gray-500 ml-2">
                            (DOB: {{ $prescription->patient->date_of_birth->format('Y-m-d') }})
                        </span>
                    </dd>
                </div>
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Prescribing Physician</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        @if($prescription->provider)
                            <a href="{{ route('physicians.show', $prescription->provider->provider_id) }}"
                               class="text-medical-blue hover:underline">
                                {{ $prescription->provider->full_name }}
                            </a>
                            <span class="text-gray-500 ml-2">{{ $prescription->provider->specialty }}</span>
                        @else
                            Not specified
                        @endif
                    </dd>
                </div>
                @if($prescription->encounter)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Related Appointment</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <a href="{{ route('appointments.show', $prescription->encounter->encounter_id) }}"
                           class="text-medical-blue hover:underline">
                            {{ $prescription->encounter->encounter_date->format('F j, Y') }} - {{ $prescription->encounter->encounter_type }}
                        </a>
                    </dd>
                </div>
                @endif
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Prescribed Date</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ $prescription->prescribed_date ? $prescription->prescribed_date->format('F j, Y') : 'Not recorded' }}
                    </dd>
                </div>
            </dl>
        </div>
    </div>

    <!-- Medication Information -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Medication Information</h3>
        </div>
        <div class="border-t border-gray-200">
            <dl>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Medication Name</dt>
                    <dd class="mt-1 text-sm font-semibold text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ $prescription->medication_name }}
                    </dd>
                </div>
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Dosage</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->dosage }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Frequency</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->frequency }}</dd>
                </div>
                @if($prescription->route)
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Route of Administration</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->route }}</dd>
                </div>
                @endif
                @if($prescription->quantity)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Quantity</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->quantity }}</dd>
                </div>
                @endif
                @if($prescription->refills !== null)
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Refills Allowed</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->refills }}</dd>
                </div>
                @endif
                @if($prescription->duration)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Duration</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->duration }}</dd>
                </div>
                @endif
            </dl>
        </div>
    </div>

    <!-- Treatment Dates -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Treatment Timeline</h3>
        </div>
        <div class="border-t border-gray-200">
            <dl>
                @if($prescription->start_date)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Start Date</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ $prescription->start_date->format('F j, Y') }}
                    </dd>
                </div>
                @endif
                @if($prescription->end_date)
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">End Date</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {{ $prescription->end_date->format('F j, Y') }}
                    </dd>
                </div>
                @endif
            </dl>
        </div>
    </div>

    <!-- Instructions -->
    @if($prescription->instructions)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Patient Instructions</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            <p class="text-sm text-gray-700 whitespace-pre-line">{{ $prescription->instructions }}</p>
        </div>
    </div>
    @endif

    <!-- Pharmacy Information -->
    @if($prescription->pharmacy_name || $prescription->pharmacy_address || $prescription->pharmacy_phone)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Pharmacy Information</h3>
        </div>
        <div class="border-t border-gray-200">
            <dl>
                @if($prescription->pharmacy_name)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Pharmacy Name</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->pharmacy_name }}</dd>
                </div>
                @endif
                @if($prescription->pharmacy_address)
                <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Address</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->pharmacy_address }}</dd>
                </div>
                @endif
                @if($prescription->pharmacy_phone)
                <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Phone</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ $prescription->pharmacy_phone }}</dd>
                </div>
                @endif
            </dl>
        </div>
    </div>
    @endif

    <!-- Notes -->
    @if($prescription->notes)
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Additional Notes</h3>
        </div>
        <div class="px-4 py-5 sm:px-6">
            <p class="text-sm text-gray-700 whitespace-pre-line">{{ $prescription->notes }}</p>
        </div>
    </div>
    @endif
</div>
@endsection
