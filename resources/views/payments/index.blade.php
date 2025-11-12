@extends('layouts.app')

@section('title', 'Payment History')

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
                <h1 class="text-3xl font-bold text-gray-900">Payment History</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                Patient: <span class="font-medium">{{ $patient->full_name }}</span>
            </p>
        </div>
    </div>

    <!-- Payment Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <!-- Total Payments Card -->
        <div class="bg-gradient-to-br from-green-50 to-emerald-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="ml-4 w-0 flex-1">
                        <dl>
                            <dt class="text-xs font-medium text-green-900 truncate">Total Paid</dt>
                            <dd class="text-xl font-bold text-green-900">${{ number_format($stats['total_payments'], 2) }}</dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Payment Count Card -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                        </svg>
                    </div>
                    <div class="ml-4 w-0 flex-1">
                        <dl>
                            <dt class="text-xs font-medium text-blue-900 truncate">Transactions</dt>
                            <dd class="text-xl font-bold text-blue-900">{{ $stats['payment_count'] }}</dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Pending Payments Card -->
        <div class="bg-gradient-to-br from-yellow-50 to-amber-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="ml-4 w-0 flex-1">
                        <dl>
                            <dt class="text-xs font-medium text-yellow-900 truncate">Pending</dt>
                            <dd class="text-xl font-bold text-yellow-900">${{ number_format($stats['pending_payments'], 2) }}</dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Last Payment Card -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-md overflow-hidden">
            <div class="px-6 py-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-10 w-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                    </div>
                    <div class="ml-4 w-0 flex-1">
                        <dl>
                            <dt class="text-xs font-medium text-purple-900 truncate">Last Payment</dt>
                            <dd class="text-xs font-bold text-purple-900">
                                @if($stats['last_payment_date'])
                                    {{ \Carbon\Carbon::parse($stats['last_payment_date'])->format('M d, Y') }}
                                @else
                                    No payments
                                @endif
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Payment History Timeline -->
    <div class="bg-white shadow-xl rounded-xl overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
            <h3 class="text-xl font-bold text-gray-900 flex items-center">
                <svg class="w-6 h-6 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                Transaction History
            </h3>
            <p class="mt-1 text-sm text-gray-600">Complete history of all payments made</p>
        </div>

        <div class="overflow-x-auto">
            @forelse($payments as $payment)
                <div class="border-b border-gray-200 hover:bg-gradient-to-r hover:from-gray-50 hover:to-white transition-all">
                    <div class="px-6 py-5">
                        <div class="flex items-center justify-between">
                            <div class="flex items-start space-x-4 flex-1">
                                <!-- Payment Icon -->
                                <div class="flex-shrink-0">
                                    @php
                                        $iconColors = [
                                            'Completed' => 'bg-green-100 text-green-600',
                                            'Pending' => 'bg-yellow-100 text-yellow-600',
                                            'Failed' => 'bg-red-100 text-red-600',
                                            'Refunded' => 'bg-gray-100 text-gray-600',
                                        ];
                                        $iconColor = $iconColors[$payment->status] ?? 'bg-gray-100 text-gray-600';
                                    @endphp
                                    <div class="w-12 h-12 rounded-full {{ $iconColor }} flex items-center justify-center">
                                        @if($payment->status === 'Completed')
                                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                            </svg>
                                        @elseif($payment->status === 'Pending')
                                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                            </svg>
                                        @elseif($payment->status === 'Failed')
                                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                            </svg>
                                        @else
                                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
                                            </svg>
                                        @endif
                                    </div>
                                </div>

                                <!-- Payment Details -->
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-3">
                                        <p class="text-base font-bold text-gray-900">
                                            Payment #{{ $payment->payment_id }}
                                        </p>
                                        @php
                                            $statusColors = [
                                                'Completed' => 'bg-green-100 text-green-800 border-green-200',
                                                'Pending' => 'bg-yellow-100 text-yellow-800 border-yellow-200',
                                                'Failed' => 'bg-red-100 text-red-800 border-red-200',
                                                'Refunded' => 'bg-gray-100 text-gray-800 border-gray-200',
                                            ];
                                            $statusColor = $statusColors[$payment->status] ?? 'bg-gray-100 text-gray-800 border-gray-200';
                                        @endphp
                                        <span class="px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full border {{ $statusColor }}">
                                            {{ $payment->status }}
                                        </span>
                                    </div>

                                    <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
                                        <span class="inline-flex items-center">
                                            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                            </svg>
                                            {{ $payment->payment_date->format('M d, Y h:i A') }}
                                        </span>

                                        @php
                                            $methodIcons = [
                                                'Credit Card' => 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
                                                'Debit Card' => 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
                                                'Cash' => 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
                                                'Check' => 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
                                                'Bank Transfer' => 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4',
                                            ];
                                            $methodIcon = $methodIcons[$payment->payment_method] ?? 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z';
                                        @endphp
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{{ $methodIcon }}"/>
                                            </svg>
                                            {{ $payment->payment_method }}
                                        </span>

                                        @if($payment->transaction_id)
                                            <span class="inline-flex items-center text-xs">
                                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
                                                </svg>
                                                TXN: {{ $payment->transaction_id }}
                                            </span>
                                        @endif
                                    </div>

                                    @if($payment->billing)
                                        <div class="mt-2">
                                            <span class="text-xs text-gray-500">
                                                Applied to Invoice:
                                                <a href="{{ route('billing.show', [$patient->patient_id, $payment->billing_id]) }}"
                                                   class="font-medium text-blue-600 hover:text-blue-800 hover:underline">
                                                    #{{ $payment->billing->invoice_number }}
                                                </a>
                                            </span>
                                        </div>
                                    @endif

                                    @if($payment->notes)
                                        <div class="mt-2 text-xs text-gray-600 italic">
                                            {{ $payment->notes }}
                                        </div>
                                    @endif
                                </div>
                            </div>

                            <!-- Amount -->
                            <div class="ml-6 flex items-center space-x-4">
                                <div class="text-right">
                                    <p class="text-2xl font-bold text-gray-900">
                                        ${{ number_format($payment->amount, 2) }}
                                    </p>
                                </div>

                                <a href="{{ route('payments.show', [$patient->patient_id, $payment->payment_id]) }}"
                                   class="inline-flex items-center px-3 py-2 border border-green-600 text-xs font-medium rounded-md text-green-600 bg-white hover:bg-green-50 transition-colors">
                                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                    </svg>
                                    Receipt
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            @empty
                <div class="px-6 py-12 text-center">
                    <svg class="mx-auto h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">No payment history</h3>
                    <p class="mt-2 text-sm text-gray-500">This patient has no payment transactions on file.</p>
                </div>
            @endforelse
        </div>

        <!-- Pagination -->
        @if($payments->hasPages())
            <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                {{ $payments->links() }}
            </div>
        @endif
    </div>
</div>
@endsection
