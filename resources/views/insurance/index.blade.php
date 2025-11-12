@extends('layouts.app')

@section('title', 'Insurance Information')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <div class="flex items-center gap-3">
                <a href="{{ route('patients.show', $patient->patient_id) }}"
                   class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                </a>
                <h1 class="text-3xl font-bold text-gray-900">Insurance Coverage</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                Patient: <span class="font-medium">{{ $patient->full_name }}</span>
            </p>
        </div>
    </div>

    @if($primaryInsurance)
        <!-- Primary Insurance Card -->
        <div class="mb-8">
            <div class="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl shadow-2xl overflow-hidden">
                <div class="px-8 py-6">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center space-x-3">
                            <div class="bg-white bg-opacity-20 rounded-full p-2">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                                </svg>
                            </div>
                            <div>
                                <p class="text-white text-xs font-medium opacity-90">PRIMARY INSURANCE</p>
                                <h2 class="text-white text-2xl font-bold">{{ $primaryInsurance->provider_name }}</h2>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-white bg-opacity-20 rounded-lg text-white text-sm font-bold">
                            Active
                        </span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                        <div class="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
                            <p class="text-white text-xs opacity-75 mb-1">Policy Number</p>
                            <p class="text-white text-lg font-mono font-bold">{{ $primaryInsurance->policy_number }}</p>
                        </div>

                        @if($primaryInsurance->group_number)
                        <div class="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
                            <p class="text-white text-xs opacity-75 mb-1">Group Number</p>
                            <p class="text-white text-lg font-mono font-bold">{{ $primaryInsurance->group_number }}</p>
                        </div>
                        @endif

                        <div class="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
                            <p class="text-white text-xs opacity-75 mb-1">Plan Type</p>
                            <p class="text-white text-lg font-bold">{{ $primaryInsurance->plan_type ?? 'Not specified' }}</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        <div class="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
                            <p class="text-white text-xs opacity-75 mb-1">Subscriber Name</p>
                            <p class="text-white text-base font-semibold">{{ $primaryInsurance->subscriber_name }}</p>
                            <p class="text-white text-xs opacity-75 mt-1">
                                Relationship: <span class="font-medium">{{ $primaryInsurance->subscriber_relationship }}</span>
                            </p>
                        </div>

                        <div class="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
                            <p class="text-white text-xs opacity-75 mb-1">Coverage Period</p>
                            <p class="text-white text-base font-semibold">
                                {{ $primaryInsurance->effective_date->format('M d, Y') }}
                                @if($primaryInsurance->termination_date)
                                    - {{ $primaryInsurance->termination_date->format('M d, Y') }}
                                @else
                                    - Present
                                @endif
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    @endif

    <!-- Secondary/Additional Insurance -->
    @if($secondaryInsurances->count() > 0)
        <div class="mb-8">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <svg class="w-6 h-6 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                Additional Coverage
            </h3>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                @foreach($secondaryInsurances as $insurance)
                    <div class="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-200 hover:border-blue-400 transition-colors">
                        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                            <div class="flex items-center justify-between">
                                <h4 class="text-lg font-bold text-gray-900">{{ $insurance->provider_name }}</h4>
                                <span class="px-3 py-1 bg-gray-200 text-gray-700 text-xs font-semibold rounded-full">
                                    Secondary
                                </span>
                            </div>
                        </div>

                        <div class="px-6 py-5">
                            <dl class="grid grid-cols-2 gap-4">
                                <div class="col-span-2">
                                    <dt class="text-xs font-medium text-gray-500 uppercase tracking-wide">Policy Number</dt>
                                    <dd class="mt-1 text-base font-mono font-bold text-gray-900">{{ $insurance->policy_number }}</dd>
                                </div>

                                @if($insurance->group_number)
                                <div>
                                    <dt class="text-xs font-medium text-gray-500 uppercase tracking-wide">Group Number</dt>
                                    <dd class="mt-1 text-sm font-mono font-semibold text-gray-900">{{ $insurance->group_number }}</dd>
                                </div>
                                @endif

                                <div>
                                    <dt class="text-xs font-medium text-gray-500 uppercase tracking-wide">Plan Type</dt>
                                    <dd class="mt-1 text-sm font-semibold text-gray-900">{{ $insurance->plan_type ?? 'N/A' }}</dd>
                                </div>

                                <div class="col-span-2">
                                    <dt class="text-xs font-medium text-gray-500 uppercase tracking-wide">Subscriber</dt>
                                    <dd class="mt-1 text-sm font-semibold text-gray-900">
                                        {{ $insurance->subscriber_name }}
                                        <span class="text-gray-500 text-xs ml-1">({{ $insurance->subscriber_relationship }})</span>
                                    </dd>
                                </div>

                                <div class="col-span-2">
                                    <dt class="text-xs font-medium text-gray-500 uppercase tracking-wide">Coverage Period</dt>
                                    <dd class="mt-1 text-sm font-semibold text-gray-900">
                                        {{ $insurance->effective_date->format('M d, Y') }}
                                        @if($insurance->termination_date)
                                            - {{ $insurance->termination_date->format('M d, Y') }}
                                        @else
                                            - Present
                                        @endif
                                    </dd>
                                </div>
                            </dl>
                        </div>

                        <div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
                            <a href="{{ route('insurance.show', [$patient->patient_id, $insurance->insurance_id]) }}"
                               class="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center">
                                View Full Details
                                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                </svg>
                            </a>
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    <!-- All Insurance Policies Table -->
    @if($insurances->count() > 0)
        <div class="bg-white shadow-xl rounded-xl overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                <h3 class="text-xl font-bold text-gray-900 flex items-center">
                    <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    Complete Insurance History
                </h3>
                <p class="mt-1 text-sm text-gray-600">All insurance policies including expired coverage</p>
            </div>

            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Policy Info</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coverage Period</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        @foreach($insurances as $insurance)
                            <tr class="hover:bg-gray-50 transition-colors">
                                <td class="px-6 py-4">
                                    <div class="flex items-center">
                                        <div class="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                                            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                                            </svg>
                                        </div>
                                        <div class="ml-4">
                                            <div class="text-sm font-bold text-gray-900">{{ $insurance->provider_name }}</div>
                                            @if($insurance->plan_type)
                                                <div class="text-xs text-gray-500">{{ $insurance->plan_type }}</div>
                                            @endif
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="text-sm">
                                        <div class="font-mono font-semibold text-gray-900">{{ $insurance->policy_number }}</div>
                                        @if($insurance->group_number)
                                            <div class="text-xs text-gray-500">Group: {{ $insurance->group_number }}</div>
                                        @endif
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">
                                        {{ $insurance->effective_date->format('M d, Y') }}
                                    </div>
                                    <div class="text-xs text-gray-500">
                                        @if($insurance->termination_date)
                                            to {{ $insurance->termination_date->format('M d, Y') }}
                                        @else
                                            Present
                                        @endif
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex flex-col space-y-1">
                                        @if($insurance->is_primary)
                                            <span class="px-2 py-1 inline-flex text-xs leading-4 font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                                                Primary
                                            </span>
                                        @else
                                            <span class="px-2 py-1 inline-flex text-xs leading-4 font-semibold rounded-full bg-gray-100 text-gray-800 border border-gray-200">
                                                Secondary
                                            </span>
                                        @endif

                                        @php
                                            $isActive = !$insurance->termination_date || $insurance->termination_date->isFuture();
                                        @endphp
                                        @if($isActive)
                                            <span class="px-2 py-1 inline-flex text-xs leading-4 font-semibold rounded-full bg-green-100 text-green-800 border border-green-200">
                                                Active
                                            </span>
                                        @else
                                            <span class="px-2 py-1 inline-flex text-xs leading-4 font-semibold rounded-full bg-red-100 text-red-800 border border-red-200">
                                                Expired
                                            </span>
                                        @endif
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm">
                                    <a href="{{ route('insurance.show', [$patient->patient_id, $insurance->insurance_id]) }}"
                                       class="inline-flex items-center px-3 py-1.5 border border-blue-600 text-xs font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 transition-colors">
                                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                        </svg>
                                        View
                                    </a>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    @else
        <!-- No Insurance Card -->
        <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl shadow-lg overflow-hidden border-2 border-dashed border-gray-300">
            <div class="px-8 py-12 text-center">
                <div class="mx-auto h-16 w-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                    <svg class="h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">No Insurance Information</h3>
                <p class="text-gray-600">This patient has no insurance policies on file.</p>
            </div>
        </div>
    @endif
</div>
@endsection
