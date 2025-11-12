@extends('layouts.app')

@section('title', 'Invoice Details')

@section('content')
<div class="px-4 sm:px-0 max-w-5xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
        <a href="{{ route('billing.index', $patient->patient_id) }}"
           class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Back to Billing
        </a>
        <h1 class="text-3xl font-bold text-gray-900">Invoice #{{ $billing->invoice_number }}</h1>
    </div>

    <!-- Invoice -->
    <div class="bg-white shadow-2xl rounded-2xl overflow-hidden">
        <!-- Invoice Header -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-700 px-8 py-6 text-white">
            <div class="flex justify-between items-start">
                <div>
                    <h2 class="text-3xl font-bold mb-2">INVOICE</h2>
                    <p class="text-blue-100">InHealth EHR System</p>
                </div>
                <div class="text-right">
                    @php
                        $statusColors = [
                            'Paid' => 'bg-green-500',
                            'Partial' => 'bg-yellow-500',
                            'Pending' => 'bg-blue-400',
                            'Overdue' => 'bg-red-500',
                            'Cancelled' => 'bg-gray-500',
                        ];
                        $color = $statusColors[$billing->status] ?? 'bg-gray-500';
                    @endphp
                    <span class="inline-block px-4 py-2 {{ $color }} text-white font-bold rounded-lg text-lg">
                        {{ $billing->status }}
                    </span>
                    <p class="text-blue-100 mt-2 text-sm">Invoice #{{ $billing->invoice_number }}</p>
                </div>
            </div>
        </div>

        <!-- Patient & Billing Info -->
        <div class="px-8 py-6 bg-gray-50 border-b border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Bill To</h3>
                    <div class="text-gray-900">
                        <p class="text-lg font-bold">{{ $patient->full_name }}</p>
                        @if($patient->address_street)
                            <p class="text-sm mt-1">{{ $patient->address_street }}</p>
                            <p class="text-sm">{{ $patient->address_city }}, {{ $patient->address_state }} {{ $patient->address_zip }}</p>
                        @endif
                        @if($patient->phone_number)
                            <p class="text-sm mt-1">{{ $patient->phone_number }}</p>
                        @endif
                        @if($patient->email)
                            <p class="text-sm">{{ $patient->email }}</p>
                        @endif
                    </div>
                </div>

                <div class="text-right">
                    <div class="space-y-2">
                        <div>
                            <span class="text-sm text-gray-500">Billing Date:</span>
                            <span class="text-sm font-semibold text-gray-900 ml-2">{{ $billing->billing_date->format('M d, Y') }}</span>
                        </div>
                        <div>
                            <span class="text-sm text-gray-500">Due Date:</span>
                            <span class="text-sm font-semibold text-gray-900 ml-2">{{ $billing->due_date->format('M d, Y') }}</span>
                        </div>
                        @if($billing->encounter)
                            <div>
                                <span class="text-sm text-gray-500">Encounter:</span>
                                <span class="text-sm font-semibold text-gray-900 ml-2">{{ $billing->encounter->encounter_type }}</span>
                            </div>
                            <div>
                                <span class="text-sm text-gray-500">Date of Service:</span>
                                <span class="text-sm font-semibold text-gray-900 ml-2">{{ $billing->encounter->encounter_date->format('M d, Y') }}</span>
                            </div>
                        @endif
                    </div>
                </div>
            </div>
        </div>

        <!-- Billing Items -->
        <div class="px-8 py-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Services & Charges</h3>

            <div class="overflow-hidden border border-gray-200 rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-100">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Service Code</th>
                            <th class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Description</th>
                            <th class="px-4 py-3 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">Qty</th>
                            <th class="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Unit Price</th>
                            <th class="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Total</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        @forelse($billing->billingItems as $item)
                            <tr class="hover:bg-gray-50">
                                <td class="px-4 py-4 text-sm font-mono font-semibold text-gray-900">
                                    {{ $item->service_code }}
                                </td>
                                <td class="px-4 py-4 text-sm text-gray-900">
                                    <div class="font-medium">{{ $item->service_description }}</div>
                                    @if($item->notes)
                                        <div class="text-xs text-gray-500 mt-1">{{ $item->notes }}</div>
                                    @endif
                                </td>
                                <td class="px-4 py-4 text-sm text-center font-semibold text-gray-900">
                                    {{ $item->quantity }}
                                </td>
                                <td class="px-4 py-4 text-sm text-right text-gray-900">
                                    ${{ number_format($item->unit_price, 2) }}
                                </td>
                                <td class="px-4 py-4 text-sm text-right font-semibold text-gray-900">
                                    ${{ number_format($item->total_price, 2) }}
                                </td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="5" class="px-4 py-8 text-center text-sm text-gray-500">
                                    No billing items found
                                </td>
                            </tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Totals -->
        <div class="px-8 py-6 bg-gray-50 border-t border-gray-200">
            <div class="max-w-md ml-auto space-y-3">
                <div class="flex justify-between items-center">
                    <span class="text-base text-gray-700">Subtotal:</span>
                    <span class="text-base font-semibold text-gray-900">${{ number_format($billing->total_amount, 2) }}</span>
                </div>

                @if($billing->amount_paid > 0)
                    <div class="flex justify-between items-center text-green-700">
                        <span class="text-base">Amount Paid:</span>
                        <span class="text-base font-semibold">-${{ number_format($billing->amount_paid, 2) }}</span>
                    </div>
                @endif

                <div class="pt-3 border-t-2 border-gray-300">
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold text-gray-900">Balance Due:</span>
                        <span class="text-2xl font-bold {{ $billing->amount_due > 0 ? 'text-orange-600' : 'text-green-600' }}">
                            ${{ number_format($billing->amount_due, 2) }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Payment History -->
        @if($billing->payments->count() > 0)
            <div class="px-8 py-6 border-t border-gray-200">
                <h3 class="text-lg font-bold text-gray-900 mb-4">Payment History</h3>

                <div class="space-y-3">
                    @foreach($billing->payments as $payment)
                        <div class="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                            <div class="flex items-center space-x-3">
                                <div class="flex-shrink-0 w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
                                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                </div>
                                <div>
                                    <p class="text-sm font-semibold text-gray-900">
                                        Payment received on {{ $payment->payment_date->format('M d, Y') }}
                                    </p>
                                    <p class="text-xs text-gray-600">
                                        Method: {{ $payment->payment_method }}
                                        @if($payment->transaction_id)
                                            • TXN: {{ $payment->transaction_id }}
                                        @endif
                                    </p>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="text-lg font-bold text-green-700">${{ number_format($payment->amount, 2) }}</p>
                                <span class="text-xs px-2 py-1 bg-green-200 text-green-800 rounded-full font-semibold">
                                    {{ $payment->status }}
                                </span>
                            </div>
                        </div>
                    @endforeach
                </div>
            </div>
        @endif

        <!-- Notes -->
        @if($billing->notes)
            <div class="px-8 py-6 bg-yellow-50 border-t border-yellow-200">
                <h3 class="text-sm font-bold text-yellow-900 mb-2">Notes</h3>
                <p class="text-sm text-yellow-800">{{ $billing->notes }}</p>
            </div>
        @endif

        <!-- Footer -->
        <div class="px-8 py-6 bg-gray-100 border-t border-gray-200 text-center">
            <p class="text-sm text-gray-600">
                Thank you for choosing InHealth EHR System
            </p>
            <p class="text-xs text-gray-500 mt-1">
                For billing inquiries, please contact our billing department
            </p>
        </div>
    </div>
</div>
@endsection
