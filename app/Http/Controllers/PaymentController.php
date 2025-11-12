<?php

namespace App\Http\Controllers;

use App\Models\Patient;
use App\Models\Payment;
use Illuminate\Http\Request;
use Illuminate\View\View;

class PaymentController extends Controller
{
    /**
     * Display payment history for a patient
     */
    public function index(Patient $patient): View
    {
        $payments = $patient->payments()
            ->with(['billing'])
            ->orderBy('payment_date', 'desc')
            ->paginate(15);

        $stats = [
            'total_payments' => $patient->payments()->where('status', 'Completed')->sum('amount'),
            'payment_count' => $patient->payments()->where('status', 'Completed')->count(),
            'pending_payments' => $patient->payments()->where('status', 'Pending')->sum('amount'),
            'last_payment_date' => $patient->payments()->where('status', 'Completed')->max('payment_date'),
        ];

        return view('payments.index', compact('patient', 'payments', 'stats'));
    }

    /**
     * Display a specific payment
     */
    public function show(Patient $patient, Payment $payment): View
    {
        $payment->load(['billing', 'patient']);

        return view('payments.show', compact('patient', 'payment'));
    }
}
