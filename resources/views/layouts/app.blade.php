<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'InHealth EHR') - Electronic Health Record System</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="bg-gray-100">
    <!-- Navigation -->
    <nav class="bg-medical-blue shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <div class="flex-shrink-0 flex items-center">
                        <a href="{{ route('dashboard') }}" class="text-white font-bold text-xl">
                            InHealth EHR
                        </a>
                    </div>
                    <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <a href="{{ route('dashboard') }}"
                           class="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                            Dashboard
                        </a>
                        <a href="{{ route('patients.index') }}"
                           class="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                            Patients
                        </a>
                        <a href="{{ route('providers.index') }}"
                           class="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                            Providers
                        </a>
                        <a href="{{ route('encounters.index') }}"
                           class="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                            Encounters
                        </a>
                        <a href="{{ route('prescriptions.index') }}"
                           class="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                            Prescriptions
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    @if(session('success'))
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
                <span class="block sm:inline">{{ session('success') }}</span>
            </div>
        </div>
    @endif

    @if(session('error'))
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <span class="block sm:inline">{{ session('error') }}</span>
            </div>
        </div>
    @endif

    <!-- Main Content -->
    <main class="py-10">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            @yield('content')
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-10">
        <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <p class="text-center text-gray-500 text-sm">
                &copy; {{ date('Y') }} InTAM Health Inc. All rights reserved.
            </p>
        </div>
    </footer>
</body>
</html>
