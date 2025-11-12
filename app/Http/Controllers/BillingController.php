<?php

namespace App\Http\Controllers;

use App\Models\Patient;
use App\Models\Billing;
use Illuminate\Http\Request;
use Illuminate\View\View;

class BillingController extends Controller
{
    /**
     * Display billing information for a patient
     */
    public function index(Patient $patient): View
    {
        $billings = $patient->billings()
            ->with(['billingItems', 'encounter', 'payments'])
            ->orderBy('billing_date', 'desc')
            ->paginate(10);

        $totalBilled = $patient->billings()->sum('total_amount');
        $totalPaid = $patient->billings()->sum('amount_paid');
        $totalDue = $patient->billings()->sum('amount_due');

        return view('billing.index', compact('patient', 'billings', 'totalBilled', 'totalPaid', 'totalDue'));
    }

    /**
     * Display a specific billing invoice
     */
    public function show(Patient $patient, Billing $billing): View
    {
        $billing->load(['billingItems', 'encounter', 'payments', 'patient']);

        return view('billing.show', compact('patient', 'billing'));
    }
}
