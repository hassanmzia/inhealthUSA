@extends('layouts.app')

@section('title', 'Payment Receipt')

@section('content')
<div class="px-4 sm:px-0 max-w-3xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
        <a href="{{ route('payments.index', $patient->patient_id) }}"
           class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Back to Payment History
        </a>
        <h1 class="text-3xl font-bold text-gray-900">Payment Receipt</h1>
    </div>

    <!-- Receipt -->
    <div class="bg-white shadow-2xl rounded-2xl overflow-hidden">
        <!-- Receipt Header -->
        <div class="bg-gradient-to-r from-green-600 to-emerald-700 px-8 py-8 text-white text-center">
            <div class="w-20 h-20 bg-white bg-opacity-20 rounded-full mx-auto flex items-center justify-center mb-4">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
            </div>
            <h2 class="text-4xl font-bold mb-2">${{ number_format($payment->amount, 2) }}</h2>
            <p class="text-green-100 text-lg">Payment {{ $payment->status }}</p>
        </div>

        <!-- Receipt Details -->
        <div class="px-8 py-6">
            <div class="grid grid-cols-2 gap-6 mb-6">
                <div>
                    <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Transaction ID</p>
                    <p class="text-base font-mono font-bold text-gray-900">
                        {{ $payment->transaction_id ?? 'N/A' }}
                    </p>
                </div>
                <div>
                    <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Payment Date</p>
                    <p class="text-base font-semibold text-gray-900">
                        {{ $payment->payment_date->format('M d, Y h:i A') }}
                    </p>
                </div>
            </div>

            <div class="border-t border-gray-200 pt-6 mb-6">
                <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide mb-4">Patient Information</h3>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Name:</span>
                        <span class="text-sm font-semibold text-gray-900">{{ $patient->full_name }}</span>
                    </div>
                    @if($patient->phone_number)
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Phone:</span>
                            <span class="text-sm font-semibold text-gray-900">{{ $patient->phone_number }}</span>
                        </div>
                    @endif
                    @if($patient->email)
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Email:</span>
                            <span class="text-sm font-semibold text-gray-900">{{ $patient->email }}</span>
                        </div>
                    @endif
                </div>
            </div>

            <div class="border-t border-gray-200 pt-6 mb-6">
                <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide mb-4">Payment Details</h3>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Payment Method:</span>
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                            {{ $payment->payment_method }}
                        </span>
                    </div>

                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Status:</span>
                        @php
                            $statusColors = [
                                'Completed' => 'bg-green-100 text-green-800',
                                'Pending' => 'bg-yellow-100 text-yellow-800',
                                'Failed' => 'bg-red-100 text-red-800',
                                'Refunded' => 'bg-gray-100 text-gray-800',
                            ];
                            $statusColor = $statusColors[$payment->status] ?? 'bg-gray-100 text-gray-800';
                        @endphp
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold {{ $statusColor }}">
                            {{ $payment->status }}
                        </span>
                    </div>

                    @if($payment->billing)
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Applied to Invoice:</span>
                            <a href="{{ route('billing.show', [$patient->patient_id, $payment->billing_id]) }}"
                               class="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline">
                                #{{ $payment->billing->invoice_number }}
                            </a>
                        </div>
                    @endif
                </div>
            </div>

            @if($payment->notes)
                <div class="border-t border-gray-200 pt-6 mb-6">
                    <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide mb-2">Notes</h3>
                    <p class="text-sm text-gray-600">{{ $payment->notes }}</p>
                </div>
            @endif

            <!-- Amount Summary -->
            <div class="border-t-2 border-gray-300 pt-6">
                <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold text-gray-900">Total Amount Paid:</span>
                        <span class="text-3xl font-bold text-green-600">
                            ${{ number_format($payment->amount, 2) }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="px-8 py-6 bg-gray-50 border-t border-gray-200 text-center">
            <p class="text-sm text-gray-600 mb-2">
                Thank you for your payment
            </p>
            <p class="text-xs text-gray-500">
                This is your official payment receipt. Please keep for your records.
            </p>
        </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 flex justify-center space-x-4">
        <button onclick="window.print()"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
            </svg>
            Print Receipt
        </button>
    </div>
</div>
@endsection
