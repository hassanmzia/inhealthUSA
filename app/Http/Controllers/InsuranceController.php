<?php

namespace App\Http\Controllers;

use App\Models\Patient;
use App\Models\InsuranceInformation;
use Illuminate\Http\Request;
use Illuminate\View\View;

class InsuranceController extends Controller
{
    /**
     * Display insurance information for a patient
     */
    public function index(Patient $patient): View
    {
        $insurances = $patient->insurance()
            ->orderBy('is_primary', 'desc')
            ->orderBy('effective_date', 'desc')
            ->get();

        $primaryInsurance = $insurances->where('is_primary', true)->first();
        $secondaryInsurances = $insurances->where('is_primary', false);

        return view('insurance.index', compact('patient', 'insurances', 'primaryInsurance', 'secondaryInsurances'));
    }

    /**
     * Display a specific insurance policy
     */
    public function show(Patient $patient, InsuranceInformation $insurance): View
    {
        return view('insurance.show', compact('patient', 'insurance'));
    }
}
