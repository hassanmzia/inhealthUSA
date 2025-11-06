<?php

use App\Http\Controllers\DashboardController;
use App\Http\Controllers\PatientController;
use App\Http\Controllers\EncounterController;
use App\Http\Controllers\VitalSignController;
use App\Http\Controllers\DiagnosisController;
use App\Http\Controllers\PrescriptionController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/

// Dashboard
Route::get('/', [DashboardController::class, 'index'])->name('dashboard');

// Patients
Route::resource('patients', PatientController::class)->parameters([
    'patients' => 'patient:patient_id'
]);

// Encounters
Route::resource('encounters', EncounterController::class)->parameters([
    'encounters' => 'encounter:encounter_id'
]);
Route::post('encounters/{encounter}/complete', [EncounterController::class, 'complete'])
    ->name('encounters.complete');

// Vital Signs
Route::get('encounters/{encounter}/vital-signs/create', [VitalSignController::class, 'create'])
    ->name('vital-signs.create');
Route::post('encounters/{encounter}/vital-signs', [VitalSignController::class, 'store'])
    ->name('vital-signs.store');
Route::get('vital-signs/{vitalSign}/edit', [VitalSignController::class, 'edit'])
    ->name('vital-signs.edit');
Route::put('vital-signs/{vitalSign}', [VitalSignController::class, 'update'])
    ->name('vital-signs.update');

// Diagnoses
Route::get('encounters/{encounter}/diagnoses/create', [DiagnosisController::class, 'create'])
    ->name('diagnoses.create');
Route::post('encounters/{encounter}/diagnoses', [DiagnosisController::class, 'store'])
    ->name('diagnoses.store');
Route::get('diagnoses/{diagnosis}/edit', [DiagnosisController::class, 'edit'])
    ->name('diagnoses.edit');
Route::put('diagnoses/{diagnosis}', [DiagnosisController::class, 'update'])
    ->name('diagnoses.update');
Route::delete('diagnoses/{diagnosis}', [DiagnosisController::class, 'destroy'])
    ->name('diagnoses.destroy');

// Prescriptions
Route::resource('prescriptions', PrescriptionController::class)->parameters([
    'prescriptions' => 'prescription:prescription_id'
]);
Route::get('encounters/{encounter}/prescriptions/create', [PrescriptionController::class, 'create'])
    ->name('prescriptions.create.encounter');
Route::post('encounters/{encounter}/prescriptions', [PrescriptionController::class, 'store'])
    ->name('prescriptions.store.encounter');
Route::post('prescriptions/{prescription}/discontinue', [PrescriptionController::class, 'discontinue'])
    ->name('prescriptions.discontinue');

// API Routes (for frontend AJAX calls)
Route::prefix('api')->group(function () {
    Route::get('patients/search', [PatientController::class, 'search'])->name('api.patients.search');
});
