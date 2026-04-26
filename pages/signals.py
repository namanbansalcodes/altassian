"""Post-save signals: html cache, search vector, version recording.

Strategy: pre_save snapshots the prior body_md; post_save renders html,
updates search_vector via SQL, and creates a new PageVersion if body_md changed.
"""
from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Page, PageVersion
from .rendering import markdown_to_html

_PRIOR_BODY_ATTR = "_prior_body_md"


@receiver(pre_save, sender=Page)
def _capture_prior_body(sender, instance: Page, **kwargs):
    if instance.pk:
        try:
            old = Page.objects.only("body_md").get(pk=instance.pk)
            setattr(instance, _PRIOR_BODY_ATTR, old.body_md)
        except Page.DoesNotExist:
            setattr(instance, _PRIOR_BODY_ATTR, None)
    else:
        setattr(instance, _PRIOR_BODY_ATTR, None)


@receiver(post_save, sender=Page)
def _on_page_saved(sender, instance: Page, created: bool, **kwargs):
    new_html = markdown_to_html(instance.body_md or "")
    prior = getattr(instance, _PRIOR_BODY_ATTR, None)
    body_changed = created or (prior != instance.body_md)

    # Update html cache + search vector in one UPDATE without re-triggering signals.
    Page.objects.filter(pk=instance.pk).update(
        body_html_cache=new_html,
        search_vector=SearchVector("title", "body_md", config="english"),
    )

    if body_changed:
        last_n = PageVersion.objects.filter(page=instance).order_by("-version_n").values_list("version_n", flat=True).first()
        next_n = (last_n or 0) + 1
        PageVersion.objects.create(
            page=instance,
            version_n=next_n,
            body_md=instance.body_md or "",
            edited_by=instance.updated_by,
        )
