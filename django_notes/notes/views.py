from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

from .models import Note

def editor(request):
    user = request.user
    note_id = int(request.GET.get('note_id', 0))
    notes = Note.objects.filter(author=user.pk)
    
    if request.method == 'POST':
        note_id = int(request.POST.get('note_id', 0))
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        
        if note_id > 0:
            note = Note.objects.get(pk=note_id)
            note.title = title
            note.content = content
            note.save()
            messages.success(request, "Note updated successfully.")
            
            return redirect('/?note_id=%i' % note_id)
        else:
            messages.success(request, "Note created successfully.")
            note = Note.objects.create(title=title, content=content, author=user)
            
            return redirect('/?note_id=%i' % note.id)
            
    
    if note_id > 0:
       note = Note.objects.get(pk=note_id)
    else:
        note = ''
    
    context = {
        'note': note,
        'notes': notes,
        'note_id': note_id
    }
    
    return render(request, 'shared/index.html', context)

def delete_note(request, note_id):
    note = Note.objects.get(pk=note_id)
    note.delete()
    return redirect('/?docid=0')
    