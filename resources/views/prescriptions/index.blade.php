@extends('layouts.app')

@section('title', 'Prescriptions')

@section('content')
<div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Prescriptions</h1>
            <p class="mt-2 text-sm text-gray-700">E-prescribing and medication management.</p>
        </div>
        <div class="mt-4 sm:mt-0">
            <a href="{{ route('prescriptions.create') }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                New Prescription
            </a>
        </div>
    </div>

    <!-- Filters ---->
    <div class="mb-4 flex space-x-4">
        <form method="GET" action="{{ route('prescriptions.index') }}" class="flex space-x-4">
            <select name="status" class="rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue text-sm" onchange="this.form.submit()">
                <option value="">All Status</option>
                <option value="Active" {{ request('status') == 'Active' ? 'selected' : '' }}>Active</option>
                <option value="Completed" {{ request('status') == 'Completed' ? 'selected' : '' }}>Completed</option>
                <option value="Discontinued" {{ request('status') == 'Discontinued' ? 'selected' : '' }}>Discontinued</option>
                <option value="Pending" {{ request('status') == 'Pending' ? 'selected' : '' }}>Pending</option>
            </select>

            <input type="text" name="search" value="{{ request('search') }}"
                   placeholder="Search patient or medication..."
                   class="rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue text-sm">

            <button type="submit" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                Search
            </button>
        </form>
    </div>

    <!-- Prescriptions Table ---->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Medication</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dosage</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Frequency</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Date</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                @forelse($prescriptions as $prescription)
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <a href="{{ route('patients.show', $prescription->patient->patient_id) }}"
                           class="text-medical-blue hover:underline">
                            {{ $prescription->patient->full_name }}
                        </a>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {{ $prescription->medication_name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $prescription->dosage }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $prescription->frequency }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $prescription->provider->full_name ?? 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ $prescription->start_date ? $prescription->start_date->format('Y-m-d') : 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            @if($prescription->status === 'Active') bg-green-100 text-green-800
                            @elseif($prescription->status === 'Pending') bg-yellow-100 text-yellow-800
                            @elseif($prescription->status === 'Discontinued') bg-red-100 text-red-800
                            @else bg-gray-100 text-gray-800
                            @endif">
                            {{ $prescription->status }}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <a href="{{ route('prescriptions.show', $prescription->prescription_id) }}"
                           class="text-medical-blue hover:underline mr-3">View</a>
                        <a href="{{ route('prescriptions.edit', $prescription->prescription_id) }}"
                           class="text-gray-600 hover:underline">Edit</a>
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="8" class="px-6 py-4 text-center text-sm text-gray-500">
                        No prescriptions found.
                    </td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <!-- Pagination ---->
    <div class="mt-4">
        {{ $prescriptions->links() }}
    </div>
</div>
@endsection
