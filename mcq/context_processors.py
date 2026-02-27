from django.utils import timezone
from mcq.models import SpacedRevision

def revision_counter(request):
    if request.user.is_authenticated:
        # Aaj ke pending revision
        count = SpacedRevision.objects.filter(
            user=request.user, 
            next_review__lte=timezone.now(),
            is_mastered=False
        ).count()
        print("____________")
        print(count)
        
        # Kya user ne kabhi koi question galat kiya ya bookmark kiya hai? (Revision list mein hai?)
        total_in_revision = SpacedRevision.objects.filter(user=request.user).count()
        
        return {
            'rev_count': count,
            'has_started_revision': total_in_revision > 0
        }
    return {'rev_count': 0, 'has_started_revision': False}