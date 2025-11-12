@extends('layouts.app')

@section('title', 'Compose Message')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <div class="flex items-center gap-3">
                <a href="{{ route('messages.inbox', [$userType, $userId]) }}"
                   class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                </a>
                <h1 class="text-3xl font-bold text-gray-900">{{ $replyTo ? 'Reply to Message' : 'Compose Message' }}</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                User: <span class="font-medium">{{ $user->full_name }}</span>
            </p>
        </div>
    </div>

    @if($replyTo)
        <div class="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4">
            <p class="text-sm text-blue-800">
                <span class="font-semibold">Replying to:</span> {{ $replyTo->subject }}
            </p>
            <p class="text-xs text-blue-700 mt-1">
                From: {{ $replyTo->sender ? $replyTo->sender->full_name : 'Unknown' }} on {{ $replyTo->created_at->format('M d, Y h:i A') }}
            </p>
        </div>
    @endif

    <!-- Compose Form -->
    <div class="bg-white shadow sm:rounded-lg">
        <form action="{{ route('messages.store', [$userType, $userId]) }}" method="POST" class="p-6 space-y-6">
            @csrf

            @if($replyTo)
                <input type="hidden" name="parent_message_id" value="{{ $replyTo->message_id }}">
                <input type="hidden" name="recipient_type" value="{{ $replyTo->sender_type === 'App\Models\Patient' ? 'patient' : 'provider' }}">
                <input type="hidden" name="recipient_id" value="{{ $replyTo->sender_id }}">
            @endif

            <!-- Recipient -->
            @if(!$replyTo)
                <div>
                    <label for="recipient" class="block text-sm font-medium text-gray-700">To</label>
                    <select name="recipient_id" id="recipient" required
                            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-medical-blue focus:border-medical-blue sm:text-sm rounded-md @error('recipient_id') border-red-300 @enderror">
                        <option value="">Select a recipient...</option>
                        <optgroup label="Patients">
                            @foreach($patients as $patient)
                                <option value="patient-{{ $patient->patient_id }}" {{ old('recipient_id') == "patient-{$patient->patient_id}" ? 'selected' : '' }}>
                                    {{ $patient->full_name }}
                                </option>
                            @endforeach
                        </optgroup>
                        <optgroup label="Doctors">
                            @foreach($providers as $provider)
                                <option value="provider-{{ $provider->provider_id }}" {{ old('recipient_id') == "provider-{$provider->provider_id}" ? 'selected' : '' }}>
                                    {{ $provider->full_name }}
                                </option>
                            @endforeach
                        </optgroup>
                    </select>
                    @error('recipient_id')
                        <p class="mt-2 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <input type="hidden" name="recipient_type" id="recipient_type" value="{{ old('recipient_type') }}">
            @else
                <div>
                    <label class="block text-sm font-medium text-gray-700">To</label>
                    <p class="mt-1 text-sm text-gray-900">{{ $replyTo->sender ? $replyTo->sender->full_name : 'Unknown' }}</p>
                </div>
            @endif

            <!-- Subject -->
            <div>
                <label for="subject" class="block text-sm font-medium text-gray-700">Subject</label>
                <input type="text" name="subject" id="subject" required
                       value="{{ old('subject', $replyTo ? 'Re: ' . $replyTo->subject : '') }}"
                       class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-medical-blue focus:border-medical-blue sm:text-sm @error('subject') border-red-300 @enderror">
                @error('subject')
                    <p class="mt-2 text-sm text-red-600">{{ $message }}</p>
                @enderror
            </div>

            <!-- Body -->
            <div>
                <label for="body" class="block text-sm font-medium text-gray-700">Message</label>
                <textarea name="body" id="body" rows="10" required
                          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-medical-blue focus:border-medical-blue sm:text-sm @error('body') border-red-300 @enderror">{{ old('body') }}</textarea>
                @error('body')
                    <p class="mt-2 text-sm text-red-600">{{ $message }}</p>
                @enderror
            </div>

            @if($replyTo && $replyTo->body)
                <div class="border-l-4 border-gray-300 pl-4 py-2 bg-gray-50 rounded">
                    <p class="text-xs text-gray-600 mb-2">Original Message:</p>
                    <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ $replyTo->body }}</p>
                </div>
            @endif

            <!-- Actions -->
            <div class="flex items-center justify-end space-x-3">
                <a href="{{ route('messages.inbox', [$userType, $userId]) }}"
                   class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                    Cancel
                </a>
                <button type="submit"
                        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                    </svg>
                    Send Message
                </button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('recipient')?.addEventListener('change', function() {
    const value = this.value;
    if (value) {
        const [type, id] = value.split('-');
        document.getElementById('recipient_type').value = type;
        // Update the actual recipient_id to just the numeric ID
        this.name = 'recipient_id_temp';
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'recipient_id';
        hiddenInput.value = id;
        hiddenInput.id = 'recipient_id_hidden';

        // Remove old hidden input if exists
        const oldHidden = document.getElementById('recipient_id_hidden');
        if (oldHidden) oldHidden.remove();

        this.parentNode.appendChild(hiddenInput);
    }
});
</script>
@endsection
