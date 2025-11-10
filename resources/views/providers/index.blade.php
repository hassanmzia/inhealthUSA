@extends('layouts.app')

@section('title', 'Providers')

@section('content')
<div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Healthcare Providers</h1>
            <p class="mt-2 text-sm text-gray-700">Manage doctors, nurses, and medical staff.</p>
        </div>
        <div class="mt-4 sm:mt-0">
            <a href="{{ route('providers.create') }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                New Provider
            </a>
        </div>
    </div>

    <!-- Search and Filters -->
    <div class="mb-4 flex flex-col sm:flex-row gap-4">
        <form method="GET" action="{{ route('providers.index') }}" class="flex-1 flex gap-4">
            <input type="text" name="search" value="{{ request('search') }}"
                   placeholder="Search by name, specialty, email, or NPI..."
                   class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue text-sm">

            <select name="specialty" class="rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue text-sm">
                <option value="">All Specialties</option>
                @foreach($specialties as $specialty)
                    <option value="{{ $specialty }}" {{ request('specialty') == $specialty ? 'selected' : '' }}>
                        {{ $specialty }}
                    </option>
                @endforeach
            </select>

            <button type="submit" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Search
            </button>

            @if(request('search') || request('specialty'))
                <a href="{{ route('providers.index') }}" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                    Clear
                </a>
            @endif
        </form>
    </div>

    <!-- Providers Table -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Specialty</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">License #</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">NPI</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recent Encounters</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                @forelse($providers as $provider)
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="flex-shrink-0 h-10 w-10">
                                <div class="h-10 w-10 rounded-full bg-medical-blue flex items-center justify-center text-white font-bold">
                                    {{ substr($provider->first_name, 0, 1) }}{{ substr($provider->last_name, 0, 1) }}
                                </div>
                            </div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">
                                    {{ $provider->full_name }}
                                </div>
                                @if(!$provider->is_active)
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                        Inactive
                                    </span>
                                @endif
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ $provider->specialty }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $provider->license_number ?? 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $provider->npi_number ?? 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ $provider->phone ?? 'N/A' }}</div>
                        <div class="text-sm text-gray-500">{{ $provider->email ?? 'N/A' }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $provider->encounters->count() }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <a href="{{ route('providers.show', $provider->provider_id) }}"
                           class="text-medical-blue hover:underline mr-3">View</a>
                        <a href="{{ route('providers.edit', $provider->provider_id) }}"
                           class="text-gray-600 hover:underline">Edit</a>
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-sm text-gray-500">
                        No providers found.
                    </td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <!-- Pagination -->
    <div class="mt-4">
        {{ $providers->links() }}
    </div>
</div>
@endsection
