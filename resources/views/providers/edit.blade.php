@extends('layouts.app')

@section('title', 'Edit Provider')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Edit Provider</h1>
        <p class="mt-2 text-sm text-gray-700">Update provider information.</p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
        <form method="POST" action="{{ route('providers.update', $provider->provider_id) }}" class="space-y-6 p-6">
            @csrf
            @method('PUT')

            <!-- Personal Information -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="first_name" class="block text-sm font-medium text-gray-700">First Name *</label>
                        <input type="text" name="first_name" id="first_name" required
                               value="{{ old('first_name', $provider->first_name) }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('first_name') border-red-300 @enderror">
                        @error('first_name')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="last_name" class="block text-sm font-medium text-gray-700">Last Name *</label>
                        <input type="text" name="last_name" id="last_name" required
                               value="{{ old('last_name', $provider->last_name) }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('last_name') border-red-300 @enderror">
                        @error('last_name')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Professional Information -->
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Professional Information</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div class="sm:col-span-2">
                        <label for="specialty" class="block text-sm font-medium text-gray-700">Specialty *</label>
                        <input type="text" name="specialty" id="specialty" required
                               value="{{ old('specialty', $provider->specialty) }}"
                               placeholder="e.g., Cardiology, Family Medicine, Pediatrics"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('specialty') border-red-300 @enderror">
                        @error('specialty')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="license_number" class="block text-sm font-medium text-gray-700">License Number</label>
                        <input type="text" name="license_number" id="license_number"
                               value="{{ old('license_number', $provider->license_number) }}"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="npi_number" class="block text-sm font-medium text-gray-700">NPI Number</label>
                        <input type="text" name="npi_number" id="npi_number" maxlength="10"
                               value="{{ old('npi_number', $provider->npi_number) }}"
                               placeholder="10-digit NPI"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                        <p class="mt-1 text-xs text-gray-500">National Provider Identifier (10 digits)</p>
                    </div>
                </div>
            </div>

            <!-- Contact Information -->
            <div class="pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>

                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label for="phone" class="block text-sm font-medium text-gray-700">Phone Number</label>
                        <input type="tel" name="phone" id="phone"
                               value="{{ old('phone', $provider->phone) }}"
                               placeholder="(555) 555-5555"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm">
                    </div>

                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
                        <input type="email" name="email" id="email"
                               value="{{ old('email', $provider->email) }}"
                               placeholder="provider@example.com"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-medical-blue focus:ring-medical-blue sm:text-sm @error('email') border-red-300 @enderror">
                        @error('email')
                            <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-between border-t border-gray-200 pt-6">
                <div>
                    @if($provider->is_active)
                        <form method="POST" action="{{ route('providers.destroy', $provider->provider_id) }}" onsubmit="return confirm('Are you sure you want to deactivate this provider?');">
                            @csrf
                            @method('DELETE')
                            <button type="submit"
                                    class="inline-flex justify-center rounded-md border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2">
                                Deactivate Provider
                            </button>
                        </form>
                    @else
                        <form method="POST" action="{{ route('providers.activate', $provider->provider_id) }}">
                            @csrf
                            @method('PUT')
                            <button type="submit"
                                    class="inline-flex justify-center rounded-md border border-green-300 bg-white px-4 py-2 text-sm font-medium text-green-700 shadow-sm hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
                                Activate Provider
                            </button>
                        </form>
                    @endif
                </div>

                <div class="flex space-x-3">
                    <a href="{{ route('providers.show', $provider->provider_id) }}"
                       class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                        Cancel
                    </a>
                    <button type="submit"
                            class="inline-flex justify-center rounded-md border border-transparent bg-medical-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-medical-blue focus:ring-offset-2">
                        Update Provider
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>
@endsection
