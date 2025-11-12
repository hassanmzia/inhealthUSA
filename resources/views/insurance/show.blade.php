@extends('layouts.app')

@section('title', 'Insurance Policy Details')

@section('content')
<div class="px-4 sm:px-0 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
        <a href="{{ route('insurance.index', $patient->patient_id) }}"
           class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Back to Insurance
        </a>
        <h1 class="text-3xl font-bold text-gray-900">Insurance Policy Details</h1>
    </div>

    <!-- Insurance Card -->
    <div class="bg-white shadow-2xl rounded-2xl overflow-hidden mb-6">
        <!-- Card Header -->
        <div class="bg-gradient-to-br from-blue-600 to-indigo-700 px-8 py-6 text-white">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="bg-white bg-opacity-20 rounded-full p-3">
                        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                        </svg>
                    </div>
                    <div>
                        <p class="text-white text-xs font-medium opacity-90">
                            {{ $insurance->is_primary ? 'PRIMARY' : 'SECONDARY' }} INSURANCE
                        </p>
                        <h2 class="text-white text-3xl font-bold">{{ $insurance->provider_name }}</h2>
                    </div>
                </div>
                @php
                    $isActive = !$insurance->termination_date || $insurance->termination_date->isFuture();
                @endphp
                <span class="px-4 py-2 {{ $isActive ? 'bg-green-500' : 'bg-red-500' }} bg-opacity-90 rounded-lg text-white text-sm font-bold">
                    {{ $isActive ? 'Active' : 'Expired' }}
                </span>
            </div>
        </div>

        <!-- Card Body -->
        <div class="px-8 py-6">
            <!-- Policy Information -->
            <div class="mb-8">
                <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    Policy Information
                </h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Policy Number</p>
                        <p class="text-xl font-mono font-bold text-gray-900">{{ $insurance->policy_number }}</p>
                    </div>

                    @if($insurance->group_number)
                        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                            <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Group Number</p>
                            <p class="text-xl font-mono font-bold text-gray-900">{{ $insurance->group_number }}</p>
                        </div>
                    @endif

                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Plan Type</p>
                        <p class="text-base font-bold text-gray-900">{{ $insurance->plan_type ?? 'Not specified' }}</p>
                    </div>

                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Coverage Level</p>
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-bold {{ $insurance->is_primary ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800' }}">
                            {{ $insurance->is_primary ? 'Primary Coverage' : 'Secondary Coverage' }}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Subscriber Information -->
            <div class="mb-8 border-t border-gray-200 pt-6">
                <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    Subscriber Information
                </h3>

                <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <p class="text-xs text-blue-700 uppercase tracking-wide mb-1">Subscriber Name</p>
                            <p class="text-lg font-bold text-gray-900">{{ $insurance->subscriber_name }}</p>
                        </div>

                        <div>
                            <p class="text-xs text-blue-700 uppercase tracking-wide mb-1">Relationship to Patient</p>
                            <p class="text-lg font-semibold text-gray-900">{{ $insurance->subscriber_relationship }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Coverage Period -->
            <div class="mb-8 border-t border-gray-200 pt-6">
                <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    Coverage Period
                </h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-green-50 rounded-lg p-6 border border-green-200">
                        <div class="flex items-center mb-2">
                            <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <p class="text-xs text-green-700 uppercase tracking-wide font-semibold">Effective Date</p>
                        </div>
                        <p class="text-2xl font-bold text-gray-900">{{ $insurance->effective_date->format('M d, Y') }}</p>
                    </div>

                    <div class="bg-{{ $insurance->termination_date ? 'red' : 'gray' }}-50 rounded-lg p-6 border border-{{ $insurance->termination_date ? 'red' : 'gray' }}-200">
                        <div class="flex items-center mb-2">
                            <svg class="w-5 h-5 mr-2 text-{{ $insurance->termination_date ? 'red' : 'gray' }}-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
                            <p class="text-xs text-{{ $insurance->termination_date ? 'red' : 'gray' }}-700 uppercase tracking-wide font-semibold">
                                {{ $insurance->termination_date ? 'Termination Date' : 'Coverage Status' }}
                            </p>
                        </div>
                        <p class="text-2xl font-bold text-gray-900">
                            @if($insurance->termination_date)
                                {{ $insurance->termination_date->format('M d, Y') }}
                            @else
                                Ongoing
                            @endif
                        </p>
                    </div>
                </div>

                @if($isActive)
                    <div class="mt-4 bg-blue-50 border-l-4 border-blue-500 p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-blue-700">
                                    This insurance policy is currently active and providing coverage.
                                </p>
                            </div>
                        </div>
                    </div>
                @else
                    <div class="mt-4 bg-red-50 border-l-4 border-red-500 p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-red-700">
                                    This insurance policy has expired and is no longer providing active coverage.
                                </p>
                            </div>
                        </div>
                    </div>
                @endif
            </div>

            <!-- Patient Information -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    Patient Information
                </h3>

                <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Patient Name:</span>
                            <span class="text-sm font-bold text-gray-900">{{ $patient->full_name }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Date of Birth:</span>
                            <span class="text-sm font-semibold text-gray-900">{{ $patient->date_of_birth->format('M d, Y') }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Gender:</span>
                            <span class="text-sm font-semibold text-gray-900">{{ $patient->gender }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
