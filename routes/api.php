<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Models\Patient;
use App\Models\Encounter;
use App\Models\Provider;
use App\Models\Department;
use App\Models\Prescription;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

// Public API endpoints (should be protected in production)
Route::prefix('v1')->group(function () {

    // Patients API
    Route::get('/patients', function (Request $request) {
        return Patient::with(['insurance', 'emergencyContacts'])
            ->active()
            ->paginate($request->input('per_page', 20));
    });

    Route::get('/patients/{patient}', function (Patient $patient) {
        return $patient->load([
            'encounters.provider',
            'allergies',
            'prescriptions',
            'pastMedicalHistory',
            'insurance'
        ]);
    });

    // Encounters API
    Route::get('/encounters', function (Request $request) {
        return Encounter::with(['patient', 'provider', 'department'])
            ->when($request->has('status'), function ($q) use ($request) {
                $q->where('status', $request->input('status'));
            })
            ->orderBy('encounter_date', 'desc')
            ->paginate($request->input('per_page', 20));
    });

    Route::get('/encounters/{encounter}', function (Encounter $encounter) {
        return $encounter->load([
            'patient',
            'provider',
            'department',
            'chiefComplaints',
            'vitalSigns',
            'diagnoses',
            'prescriptions',
            'physicalExamination',
            'clinicalImpression',
            'treatmentPlan'
        ]);
    });

    // Providers API
    Route::get('/providers', function (Request $request) {
        return Provider::active()
            ->orderBy('last_name')
            ->paginate($request->input('per_page', 50));
    });

    // Departments API
    Route::get('/departments', function (Request $request) {
        return Department::active()
            ->orderBy('department_name')
            ->get();
    });

    // Prescriptions API
    Route::get('/prescriptions', function (Request $request) {
        return Prescription::with(['patient', 'provider'])
            ->when($request->has('patient_id'), function ($q) use ($request) {
                $q->where('patient_id', $request->input('patient_id'));
            })
            ->when($request->has('status'), function ($q) use ($request) {
                $q->where('status', $request->input('status'));
            })
            ->orderBy('prescribed_date', 'desc')
            ->paginate($request->input('per_page', 20));
    });

    // Patient Search API
    Route::get('/patients/search/{query}', function ($query) {
        return Patient::active()
            ->where(function($q) use ($query) {
                $q->where('first_name', 'like', "%{$query}%")
                  ->orWhere('last_name', 'like', "%{$query}%")
                  ->orWhere('email', 'like', "%{$query}%")
                  ->orWhere('phone_number', 'like', "%{$query}%");
            })
            ->limit(10)
            ->get();
    });
});
