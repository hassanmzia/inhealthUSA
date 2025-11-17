<?php

use App\Http\Controllers\DashboardController;
use App\Http\Controllers\PatientController;
use App\Http\Controllers\PhysicianController;
use App\Http\Controllers\AppointmentController;
use App\Http\Controllers\VitalSignController;
use App\Http\Controllers\DiagnosisController;
use App\Http\Controllers\PrescriptionController;
use App\Http\Controllers\BillingController;
use App\Http\Controllers\PaymentController;
use App\Http\Controllers\InsuranceController;
use App\Http\Controllers\DeviceController;
use App\Http\Controllers\MessageController;
use App\Http\Controllers\TreatmentPlanController;
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

// Physicians
Route::resource('physicians', PhysicianController::class)->parameters([
    'physicians' => 'provider:provider_id'
]);
Route::put('physicians/{provider}/activate', [PhysicianController::class, 'activate'])
    ->name('physicians.activate');

// Appointments
Route::resource('appointments', AppointmentController::class)->parameters([
    'appointments' => 'encounter:encounter_id'
]);
Route::post('appointments/{encounter}/complete', [AppointmentController::class, 'complete'])
    ->name('appointments.complete');

// Vital Signs
Route::get('appointments/{encounter}/vital-signs/create', [VitalSignController::class, 'create'])
    ->name('vital-signs.create');
Route::post('appointments/{encounter}/vital-signs', [VitalSignController::class, 'store'])
    ->name('vital-signs.store');
Route::get('vital-signs/{vitalSign}/edit', [VitalSignController::class, 'edit'])
    ->name('vital-signs.edit');
Route::put('vital-signs/{vitalSign}', [VitalSignController::class, 'update'])
    ->name('vital-signs.update');

// Diagnoses
Route::get('appointments/{encounter}/diagnoses/create', [DiagnosisController::class, 'create'])
    ->name('diagnoses.create');
Route::post('appointments/{encounter}/diagnoses', [DiagnosisController::class, 'store'])
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
Route::get('appointments/{encounter}/prescriptions/create', [PrescriptionController::class, 'create'])
    ->name('prescriptions.create.appointment');
Route::post('appointments/{encounter}/prescriptions', [PrescriptionController::class, 'store'])
    ->name('prescriptions.store.appointment');
Route::post('prescriptions/{prescription}/discontinue', [PrescriptionController::class, 'discontinue'])
    ->name('prescriptions.discontinue');

// Treatment Plans
Route::resource('treatment-plans', TreatmentPlanController::class)->parameters([
    'treatment-plans' => 'treatmentPlan:plan_id'
]);
Route::get('appointments/{encounter}/treatment-plans/create', [TreatmentPlanController::class, 'create'])
    ->name('treatment-plans.create.appointment');
Route::post('appointments/{encounter}/treatment-plans', [TreatmentPlanController::class, 'store'])
    ->name('treatment-plans.store.appointment');

// Billing Routes
Route::get('patients/{patient}/billing', [BillingController::class, 'index'])
    ->name('billing.index');
Route::get('patients/{patient}/billing/{billing}', [BillingController::class, 'show'])
    ->name('billing.show');

// Payment Routes
Route::get('patients/{patient}/payments', [PaymentController::class, 'index'])
    ->name('payments.index');
Route::get('patients/{patient}/payments/{payment}', [PaymentController::class, 'show'])
    ->name('payments.show');

// Insurance Routes
Route::get('patients/{patient}/insurance', [InsuranceController::class, 'index'])
    ->name('insurance.index');
Route::get('patients/{patient}/insurance/{insurance}', [InsuranceController::class, 'show'])
    ->name('insurance.show');

// Device Routes
Route::get('patients/{patient}/devices', [DeviceController::class, 'index'])
    ->name('devices.index');
Route::get('patients/{patient}/devices/create', [DeviceController::class, 'create'])
    ->name('devices.create');
Route::post('patients/{patient}/devices', [DeviceController::class, 'store'])
    ->name('devices.store');
Route::get('patients/{patient}/devices/{device}', [DeviceController::class, 'show'])
    ->name('devices.show');
Route::get('patients/{patient}/devices/{device}/edit', [DeviceController::class, 'edit'])
    ->name('devices.edit');
Route::put('patients/{patient}/devices/{device}', [DeviceController::class, 'update'])
    ->name('devices.update');
Route::delete('patients/{patient}/devices/{device}', [DeviceController::class, 'destroy'])
    ->name('devices.destroy');

// Message Routes (for both patients and providers)
Route::get('{userType}/{userId}/messages/inbox', [MessageController::class, 'inbox'])
    ->name('messages.inbox')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);
Route::get('{userType}/{userId}/messages/sent', [MessageController::class, 'sent'])
    ->name('messages.sent')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);
Route::get('{userType}/{userId}/messages/compose', [MessageController::class, 'compose'])
    ->name('messages.compose')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);
Route::post('{userType}/{userId}/messages', [MessageController::class, 'store'])
    ->name('messages.store')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);
Route::get('{userType}/{userId}/messages/{message}', [MessageController::class, 'show'])
    ->name('messages.show')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);
Route::delete('{userType}/{userId}/messages/{message}', [MessageController::class, 'destroy'])
    ->name('messages.destroy')
    ->where(['userType' => 'patient|provider', 'userId' => '[0-9]+']);

// API Routes (for frontend AJAX calls)
Route::prefix('api')->group(function () {
    Route::get('patients/search', [PatientController::class, 'search'])->name('api.patients.search');
});
