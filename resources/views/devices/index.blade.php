@extends('layouts.app')

@section('title', 'Patient Devices')

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
                <h1 class="text-3xl font-bold text-gray-900">IoT Medical Devices</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                Patient: <span class="font-medium">{{ $patient->full_name }}</span>
            </p>
        </div>
        <div class="mt-4 sm:mt-0">
            <a href="{{ route('devices.create', $patient->patient_id) }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Register New Device
            </a>
        </div>
    </div>

    @if(session('success'))
        <div class="mb-6 bg-green-50 border-l-4 border-green-500 p-4">
            <p class="text-green-800">{{ session('success') }}</p>
        </div>
    @endif

    <!-- Devices Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        @forelse($devices as $device)
            <div class="bg-white rounded-xl shadow-lg overflow-hidden border-2 {{ $device->status === 'Active' ? 'border-green-300' : 'border-gray-200' }} hover:shadow-xl transition-all">
                <!-- Device Header -->
                <div class="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="bg-white bg-opacity-20 rounded-full p-2">
                                @if($device->device_type === 'Watch')
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                @elseif($device->device_type === 'Ring' || $device->device_type === 'EarClip')
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                                    </svg>
                                @elseif($device->device_type === 'Adapter')
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                    </svg>
                                @else
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
                                    </svg>
                                @endif
                            </div>
                            <div>
                                <h3 class="text-white text-lg font-bold">{{ $device->device_name }}</h3>
                                <p class="text-blue-100 text-xs">{{ $device->device_type }}</p>
                            </div>
                        </div>
                        @php
                            $statusColors = [
                                'Active' => 'bg-green-500',
                                'Inactive' => 'bg-gray-500',
                                'Maintenance' => 'bg-yellow-500',
                                'Retired' => 'bg-red-500',
                            ];
                            $color = $statusColors[$device->status] ?? 'bg-gray-500';
                        @endphp
                        <span class="px-3 py-1 {{ $color }} text-white text-xs font-bold rounded-full">
                            {{ $device->status }}
                        </span>
                    </div>
                </div>

                <!-- Device Body -->
                <div class="px-6 py-4">
                    <div class="space-y-3">
                        <div>
                            <p class="text-xs text-gray-500 uppercase tracking-wide">Device ID</p>
                            <p class="text-sm font-mono font-semibold text-gray-900">{{ $device->device_unique_id }}</p>
                        </div>

                        @if($device->battery_level !== null)
                            <div>
                                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Battery Level</p>
                                <div class="flex items-center space-x-2">
                                    <div class="flex-1 bg-gray-200 rounded-full h-2">
                                        <div class="bg-{{ $device->battery_color }}-500 h-2 rounded-full" style="width: {{ $device->battery_level }}%"></div>
                                    </div>
                                    <span class="text-sm font-semibold text-gray-900">{{ $device->battery_level }}%</span>
                                </div>
                            </div>
                        @endif

                        @if($device->capabilities && count($device->capabilities) > 0)
                            <div>
                                <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">Capabilities</p>
                                <div class="flex flex-wrap gap-1">
                                    @foreach($device->capabilities as $capability)
                                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                            {{ $capability }}
                                        </span>
                                    @endforeach
                                </div>
                            </div>
                        @endif

                        @if($device->last_sync)
                            <div>
                                <p class="text-xs text-gray-500 uppercase tracking-wide">Last Sync</p>
                                <p class="text-sm text-gray-900">{{ $device->last_sync->diffForHumans() }}</p>
                            </div>
                        @endif
                    </div>
                </div>

                <!-- Device Footer -->
                <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex justify-between items-center">
                    <a href="{{ route('devices.show', [$patient->patient_id, $device->device_id]) }}"
                       class="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center">
                        View Details
                        <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                    </a>
                    <a href="{{ route('devices.edit', [$patient->patient_id, $device->device_id]) }}"
                       class="text-sm font-medium text-gray-600 hover:text-gray-800">
                        Edit
                    </a>
                </div>
            </div>
        @empty
            <div class="col-span-full bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl shadow-lg overflow-hidden border-2 border-dashed border-gray-300">
                <div class="px-8 py-12 text-center">
                    <div class="mx-auto h-16 w-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                        <svg class="h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">No Devices Registered</h3>
                    <p class="text-gray-600 mb-4">This patient has no IoT medical devices registered yet.</p>
                    <a href="{{ route('devices.create', $patient->patient_id) }}"
                       class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                        Register First Device
                    </a>
                </div>
            </div>
        @endforelse
    </div>
</div>
@endsection
