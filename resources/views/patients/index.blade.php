@extends('layouts.app')

@section('title', 'Patients')

@section('content')
<div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Patients</h1>
            <p class="mt-2 text-sm text-gray-700">A list of all patients in the system.</p>
        </div>
        <div class="mt-4 sm:mt-0">
            <a href="{{ route('patients.create') }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                Add Patient
            </a>
        </div>
    </div>

    <!-- Search -->
    <div class="mb-4">
        <form method="GET" action="{{ route('patients.index') }}">
            <div class="mt-1 relative rounded-md shadow-sm">
                <input type="text"
                       name="search"
                       value="{{ request('search') }}"
                       class="focus:ring-medical-blue focus:border-medical-blue block w-full pl-10 pr-12 sm:text-sm border-gray-300 rounded-md"
                       placeholder="Search patients...">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                </div>
            </div>
        </form>
    </div>

    <!-- Patients Table -->
    <div class="flex flex-col">
        <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Patient
                                </th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    DOB / Age
                                </th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Contact
                                </th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Insurance
                                </th>
                                <th scope="col" class="relative px-6 py-3">
                                    <span class="sr-only">Actions</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            @forelse($patients as $patient)
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <div>
                                            <div class="text-sm font-medium text-gray-900">
                                                {{ $patient->full_name }}
                                            </div>
                                            <div class="text-sm text-gray-500">
                                                {{ $patient->gender }}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">{{ $patient->date_of_birth->format('Y-m-d') }}</div>
                                    <div class="text-sm text-gray-500">{{ $patient->age }} years</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">{{ $patient->phone_number }}</div>
                                    <div class="text-sm text-gray-500">{{ $patient->email }}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    @if($patient->insurance->first())
                                        {{ $patient->insurance->first()->provider_name }}
                                    @else
                                        <span class="text-gray-400">No insurance</span>
                                    @endif
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <a href="{{ route('patients.show', $patient->patient_id) }}"
                                       class="text-medical-blue hover:underline mr-3">View</a>
                                    <a href="{{ route('patients.edit', $patient->patient_id) }}"
                                       class="text-gray-600 hover:underline">Edit</a>
                                </td>
                            </tr>
                            @empty
                            <tr>
                                <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                                    No patients found.
                                </td>
                            </tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Pagination -->
    <div class="mt-4">
        {{ $patients->links() }}
    </div>
</div>
@endsection
