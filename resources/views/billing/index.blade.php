@extends('layouts.app')

@section('title', 'Billing Information')

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
                <h1 class="text-3xl font-bold text-gray-900">Billing Information</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                Patient: <span class="font-medium">{{ $patient->full_name }}</span>
            </p>
        </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Total Billed Card -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-blue-900 truncate">Total Billed</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-bold text-blue-900">${{ number_format($totalBilled, 2) }}</div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Total Paid Card -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-green-900 truncate">Total Paid</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-bold text-green-900">${{ number_format($totalPaid, 2) }}</div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Balance Due Card -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-orange-900 truncate">Balance Due</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-bold text-orange-900">${{ number_format($totalDue, 2) }}</div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Billing Invoices -->
    <div class="bg-white shadow-xl rounded-xl overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <h3 class="text-xl font-bold text-gray-900 flex items-center">
                <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                Billing Invoices
            </h3>
            <p class="mt-1 text-sm text-gray-600">All billing statements and invoices</p>
        </div>

        <div class="overflow-x-auto">
            @forelse($billings as $billing)
                <div class="border-b border-gray-200 hover:bg-gray-50 transition-colors">
                    <div class="px-6 py-5">
                        <div class="flex items-center justify-between">
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center gap-4">
                                    <div>
                                        <p class="text-sm font-bold text-gray-900">
                                            Invoice #{{ $billing->invoice_number }}
                                        </p>
                                        <p class="text-xs text-gray-500 mt-1">
                                            <span class="inline-flex items-center">
                                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                                </svg>
                                                Billed: {{ $billing->billing_date->format('M d, Y') }}
                                            </span>
                                            <span class="mx-2">•</span>
                                            <span class="inline-flex items-center">
                                                Due: {{ $billing->due_date->format('M d, Y') }}
                                            </span>
                                        </p>
                                    </div>

                                    @if($billing->encounter)
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                            {{ $billing->encounter->encounter_type }}
                                        </span>
                                    @endif
                                </div>

                                @if($billing->billingItems->count() > 0)
                                    <div class="mt-3 flex flex-wrap gap-2">
                                        @foreach($billing->billingItems->take(3) as $item)
                                            <span class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700">
                                                {{ $item->service_description }} - ${{ number_format($item->total_price, 2) }}
                                            </span>
                                        @endforeach
                                        @if($billing->billingItems->count() > 3)
                                            <span class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700">
                                                +{{ $billing->billingItems->count() - 3 }} more
                                            </span>
                                        @endif
                                    </div>
                                @endif
                            </div>

                            <div class="ml-6 flex items-center space-x-6">
                                <div class="text-right">
                                    <p class="text-xs text-gray-500">Total Amount</p>
                                    <p class="text-lg font-bold text-gray-900">${{ number_format($billing->total_amount, 2) }}</p>
                                    @if($billing->amount_paid > 0)
                                        <p class="text-xs text-green-600">Paid: ${{ number_format($billing->amount_paid, 2) }}</p>
                                    @endif
                                    @if($billing->amount_due > 0)
                                        <p class="text-xs text-orange-600 font-medium">Due: ${{ number_format($billing->amount_due, 2) }}</p>
                                    @endif
                                </div>

                                <div class="flex flex-col items-center space-y-2">
                                    @php
                                        $statusColors = [
                                            'Paid' => 'bg-green-100 text-green-800 border-green-200',
                                            'Partial' => 'bg-yellow-100 text-yellow-800 border-yellow-200',
                                            'Pending' => 'bg-blue-100 text-blue-800 border-blue-200',
                                            'Overdue' => 'bg-red-100 text-red-800 border-red-200',
                                            'Cancelled' => 'bg-gray-100 text-gray-800 border-gray-200',
                                        ];
                                        $color = $statusColors[$billing->status] ?? 'bg-gray-100 text-gray-800 border-gray-200';
                                    @endphp
                                    <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border-2 {{ $color }}">
                                        {{ $billing->status }}
                                    </span>

                                    <a href="{{ route('billing.show', [$patient->patient_id, $billing->billing_id]) }}"
                                       class="inline-flex items-center px-3 py-1 border border-blue-600 text-xs font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 transition-colors">
                                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                        </svg>
                                        View Details
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            @empty
                <div class="px-6 py-12 text-center">
                    <svg class="mx-auto h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">No billing records</h3>
                    <p class="mt-2 text-sm text-gray-500">This patient has no billing invoices on file.</p>
                </div>
            @endforelse
        </div>

        <!-- Pagination -->
        @if($billings->hasPages())
            <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                {{ $billings->links() }}
            </div>
        @endif
    </div>
</div>
@endsection
