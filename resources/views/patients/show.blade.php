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

    <!-- Quick Access Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <!-- Billing Card -->
        <a href="{{ route('billing.index', $patient->patient_id) }}"
           class="group bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border-2 border-transparent hover:border-blue-300">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                    <div class="bg-blue-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                </div>
                <svg class="w-5 h-5 text-blue-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">Billing Information</h3>
            <p class="text-sm text-gray-600">View invoices and charges</p>
        </a>

        <!-- Payments Card -->
        <a href="{{ route('payments.index', $patient->patient_id) }}"
           class="group bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border-2 border-transparent hover:border-green-300">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                    <div class="bg-green-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
                        </svg>
                    </div>
                </div>
                <svg class="w-5 h-5 text-green-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">Payment History</h3>
            <p class="text-sm text-gray-600">View all transactions</p>
        </a>

        <!-- Insurance Card -->
        <a href="{{ route('insurance.index', $patient->patient_id) }}"
           class="group bg-gradient-to-br from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border-2 border-transparent hover:border-purple-300">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                    <div class="bg-purple-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                        </svg>
                    </div>
                </div>
                <svg class="w-5 h-5 text-purple-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">Insurance Coverage</h3>
            <p class="text-sm text-gray-600">View policy details</p>
        </a>

        <!-- Devices Card -->
        <a href="{{ route('devices.index', $patient->patient_id) }}"
           class="group bg-gradient-to-br from-indigo-50 to-indigo-100 hover:from-indigo-100 hover:to-indigo-200 rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border-2 border-transparent hover:border-indigo-300">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                    <div class="bg-indigo-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                </div>
                <svg class="w-5 h-5 text-indigo-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">IoT Medical Devices</h3>
            <p class="text-sm text-gray-600">Manage connected devices</p>
        </a>
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
