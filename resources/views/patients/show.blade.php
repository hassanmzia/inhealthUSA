@extends('layouts.app')

@section('title', 'Patient Details')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ $patient->full_name }}</h1>
            <p class="mt-2 text-sm text-gray-700">
                {{ $patient->gender }} | Age: {{ $patient->age }} | DOB: {{ $patient->date_of_birth->format('Y-m-d') }}
            </p>
        </div>
        <div class="mt-4 sm:mt-0 space-x-3">
            <a href="{{ route('patients.edit', $patient->patient_id) }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Edit Patient
            </a>
            <a href="{{ route('appointments.create', ['patient_id' => $patient->patient_id]) }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                New Encounter
            </a>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
            <!-- Contact Information -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-4 py-5 sm:px-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">Contact Information</h3>
                </div>
                <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
                    <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Phone</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ $patient->phone_number ?? 'N/A' }}</dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Email</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ $patient->email ?? 'N/A' }}</dd>
                        </div>
                        <div class="sm:col-span-2">
                            <dt class="text-sm font-medium text-gray-500">Address</dt>
                            <dd class="mt-1 text-sm text-gray-900">
                                @if($patient->address_street)
                                    {{ $patient->address_street }}<br>
                                    {{ $patient->address_city }}, {{ $patient->address_state }} {{ $patient->address_zip }}
                                @else
                                    N/A
                                @endif
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>

            <!-- Recent Encounters -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-4 py-5 sm:px-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">Recent Encounters</h3>
                </div>
                <div class="border-t border-gray-200">
                    <ul class="divide-y divide-gray-200">
                        @forelse($patient->encounters->take(5) as $encounter)
                        <li class="px-4 py-4 sm:px-6">
                            <div class="flex items-center justify-between">
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900">
                                        {{ $encounter->encounter_date->format('Y-m-d H:i') }}
                                    </p>
                                    <p class="text-sm text-gray-500">
                                        {{ $encounter->encounter_type }} - {{ $encounter->provider->full_name ?? 'N/A' }}
                                    </p>
                                </div>
                                <div class="flex items-center space-x-4">
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                        {{ $encounter->status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800' }}">
                                        {{ $encounter->status }}
                                    </span>
                                    <a href="{{ route('appointments.show', $encounter->encounter_id) }}"
                                       class="text-medical-blue hover:underline text-sm">View</a>
                                </div>
                            </div>
                        </li>
                        @empty
                        <li class="px-4 py-4 sm:px-6 text-center text-sm text-gray-500">
                            No encounters found.
                        </li>
                        @endforelse
                    </ul>
                </div>
            </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
            <!-- Allergies -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-4 py-5 sm:px-6 bg-red-50">
                    <h3 class="text-lg leading-6 font-medium text-red-900">Allergies</h3>
                </div>
                <div class="border-t border-gray-200">
                    <ul class="divide-y divide-gray-200">
                        @forelse($patient->allergies->where('status', 'Active') as $allergy)
                        <li class="px-4 py-3">
                            <p class="text-sm font-medium text-gray-900">{{ $allergy->allergen_name }}</p>
                            <p class="text-xs text-gray-500">
                                {{ $allergy->allergy_type }} - {{ $allergy->severity }}
                            </p>
                            @if($allergy->reaction)
                            <p class="text-xs text-gray-600 mt-1">{{ $allergy->reaction }}</p>
                            @endif
                        </li>
                        @empty
                        <li class="px-4 py-3 text-center text-sm text-gray-500">
                            No known allergies
                        </li>
                        @endforelse
                    </ul>
                </div>
            </div>

            <!-- Active Prescriptions -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-4 py-5 sm:px-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">Active Prescriptions</h3>
                </div>
                <div class="border-t border-gray-200">
                    <ul class="divide-y divide-gray-200">
                        @forelse($patient->prescriptions->where('status', 'Active')->take(5) as $prescription)
                        <li class="px-4 py-3">
                            <p class="text-sm font-medium text-gray-900">{{ $prescription->medication_name }}</p>
                            <p class="text-xs text-gray-500">
                                {{ $prescription->dosage }} - {{ $prescription->frequency }}
                            </p>
                        </li>
                        @empty
                        <li class="px-4 py-3 text-center text-sm text-gray-500">
                            No active prescriptions
                        </li>
                        @endforelse
                    </ul>
                </div>
            </div>

            <!-- Insurance -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-4 py-5 sm:px-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">Insurance</h3>
                </div>
                <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
                    @if($patient->insurance->first())
                        @php $insurance = $patient->insurance->first(); @endphp
                        <dl class="space-y-3">
                            <div>
                                <dt class="text-xs font-medium text-gray-500">Provider</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ $insurance->provider_name }}</dd>
                            </div>
                            <div>
                                <dt class="text-xs font-medium text-gray-500">Policy Number</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ $insurance->policy_number }}</dd>
                            </div>
                            <div>
                                <dt class="text-xs font-medium text-gray-500">Plan Type</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ $insurance->plan_type ?? 'N/A' }}</dd>
                            </div>
                        </dl>
                    @else
                        <p class="text-sm text-gray-500">No insurance information on file.</p>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
