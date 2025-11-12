<?php

namespace App\Http\Controllers;

use App\Models\Message;
use App\Models\Patient;
use App\Models\Provider;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class MessageController extends Controller
{
    /**
     * Display inbox messages for a user (patient or provider)
     */
    public function inbox(Request $request, $userType, $userId)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        $messages = $user->receivedMessages()
            ->with(['sender'])
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return view('messages.inbox', compact('user', 'messages', 'userType', 'userId'));
    }

    /**
     * Display sent messages for a user
     */
    public function sent(Request $request, $userType, $userId)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        $messages = $user->sentMessages()
            ->with(['recipient'])
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return view('messages.sent', compact('user', 'messages', 'userType', 'userId'));
    }

    /**
     * Show the form for composing a new message
     */
    public function compose(Request $request, $userType, $userId)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        // Get all potential recipients (patients and providers)
        $patients = Patient::active()->orderBy('last_name')->get();
        $providers = Provider::active()->orderBy('last_name')->get();

        // Check if replying to a message
        $replyTo = null;
        if ($request->has('reply_to')) {
            $replyTo = Message::find($request->reply_to);
        }

        return view('messages.compose', compact('user', 'userType', 'userId', 'patients', 'providers', 'replyTo'));
    }

    /**
     * Store a newly created message
     */
    public function store(Request $request, $userType, $userId)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        $validated = $request->validate([
            'recipient_type' => 'required|in:patient,provider',
            'recipient_id' => 'required|integer',
            'subject' => 'required|string|max:255',
            'body' => 'required|string',
            'parent_message_id' => 'nullable|exists:messages,message_id',
        ]);

        // Convert recipient_type to model class
        $recipientType = $validated['recipient_type'] === 'patient'
            ? Patient::class
            : Provider::class;

        // Verify recipient exists
        $recipient = $this->getUser($validated['recipient_type'], $validated['recipient_id']);
        if (!$recipient) {
            return back()->withErrors(['recipient_id' => 'Invalid recipient'])->withInput();
        }

        // Create message
        $message = Message::create([
            'sender_type' => get_class($user),
            'sender_id' => $userType === 'patient' ? $user->patient_id : $user->provider_id,
            'recipient_type' => $recipientType,
            'recipient_id' => $validated['recipient_id'],
            'subject' => $validated['subject'],
            'body' => $validated['body'],
            'parent_message_id' => $validated['parent_message_id'] ?? null,
        ]);

        return redirect()
            ->route('messages.sent', [$userType, $userId])
            ->with('success', 'Message sent successfully!');
    }

    /**
     * Display the specified message
     */
    public function show($userType, $userId, Message $message)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        // Verify user has access to this message
        $userClass = get_class($user);
        $userIdValue = $userType === 'patient' ? $user->patient_id : $user->provider_id;

        $hasAccess = ($message->sender_type === $userClass && $message->sender_id === $userIdValue) ||
                     ($message->recipient_type === $userClass && $message->recipient_id === $userIdValue);

        if (!$hasAccess) {
            abort(403, 'Unauthorized access to this message');
        }

        // Mark as read if user is the recipient
        if ($message->recipient_type === $userClass && $message->recipient_id === $userIdValue) {
            $message->markAsRead();
        }

        // Load relationships
        $message->load(['sender', 'recipient', 'parentMessage', 'replies.sender']);

        return view('messages.show', compact('user', 'message', 'userType', 'userId'));
    }

    /**
     * Remove the specified message from storage
     */
    public function destroy($userType, $userId, Message $message)
    {
        $user = $this->getUser($userType, $userId);

        if (!$user) {
            abort(404, 'User not found');
        }

        // Verify user owns this message (only sender can delete)
        $userClass = get_class($user);
        $userIdValue = $userType === 'patient' ? $user->patient_id : $user->provider_id;

        if ($message->sender_type !== $userClass || $message->sender_id !== $userIdValue) {
            abort(403, 'You can only delete messages you sent');
        }

        $message->delete();

        return redirect()
            ->route('messages.sent', [$userType, $userId])
            ->with('success', 'Message deleted successfully!');
    }

    /**
     * Get user instance based on type and ID
     */
    private function getUser($userType, $userId)
    {
        if ($userType === 'patient') {
            return Patient::where('patient_id', $userId)->first();
        } elseif ($userType === 'provider') {
            return Provider::where('provider_id', $userId)->first();
        }

        return null;
    }
}
