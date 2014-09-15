# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import datetime
from decimal import Decimal
from django.forms import Form
from django.forms import BooleanField
from django.forms import Textarea
from django.forms import CharField
from django.forms import ChoiceField
from django.forms import DecimalField
from django.forms import DateField
from django.forms import ValidationError
from django.forms.widgets import DateInput
from django.forms.widgets import Select
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from apps.common.templatetags.common_tags import render_percent
from apps.tags import control as tags_control
from config import settings
from apps.asset import control as asset_control

today = datetime.datetime.now().date()
mindeadline = today + datetime.timedelta(days=settings.MIN_DEADLINE)
maxdeadline = today + datetime.timedelta(days=settings.MAX_DEADLINE)
default_deadline = today + datetime.timedelta(days=settings.DEFAULT_DEADLINE)

class Bounty(Form):

  title = CharField(label=_("TITLE"))
  description = CharField(
    label=_("DESCRIPTION"),
    widget=Textarea(attrs={'class' : 'pagedownBootstrap'})
  )
  tags = CharField(label=_("TAGS"))
  asset = ChoiceField(
    choices=asset_control.get_choices(),
    label=_("ASSET"),
    initial="BTC",
    widget=Select(attrs={'class':'form-control'})
  )
  target = DecimalField(
    label=_("TARGET_REWARD"),
    help_text=_("CREATE_BOUNTY_TARGET_HELP_%(fees)s") % { 
      'fees' : render_percent(settings.FEES)
    },
    decimal_places=8
  )
  deadline = DateField(
    label=_("DEADLINE"),
    help_text=_("CREATE_BOUNTY_DEADLINE_HELP_%(min)s_%(max)s") % { 
      'min' : str(mindeadline),
      'max' : str(maxdeadline)
    },
    widget=DateInput(attrs={'class' : 'datepicker'}),
  )

  def clean_tags(self):
    tagsstr = self.cleaned_data["tags"]
    taglist = tags_control.tagsstr_to_taglist(tagsstr)
    if len(taglist) < 2:
      raise ValidationError(_("ERROR_AT_LEAST_TWO_TAGS_REQUIRED"))
    for tag in taglist:
      if not tags_control.valid_format(tag):
        raise ValidationError(_("ERROR_INVALID_TAG_FORMAT"))
    return tags_control.taglist_to_tagsstr(taglist)

  def clean_deadline(self):
    deadline = self.cleaned_data["deadline"]
    if deadline < mindeadline:
      args = { "min" : str(mindeadline) }
      raise ValidationError(_("ERROR_DEADLINE_LESS_THEN_MIN_%(min)s") % args)
    if deadline > maxdeadline:
      args = { "max" : str(maxdeadline) }
      raise ValidationError(_("ERROR_DEADLINE_GREATER_THEN_MAX_%(max)s") % args)

    return deadline

  def clean_target(self):
    target = self.cleaned_data["target"]
    if target < Decimal("0.0"):
      raise ValidationError(_("ERROR_TARGET_REWARD_LESS_THEN_ZERO"))
    return target

class CreateBounty(Bounty):

  terms = BooleanField(label=mark_safe(_("ACCEPT_TERMS")), initial=False)

  def __init__(self, *args, **kwargs):
    super(CreateBounty, self).__init__(*args, **kwargs)
    self.fields["deadline"].initial = default_deadline
    self.fields["target"].initial = 0.0

class EditBounty(Bounty):

  def __init__(self, *args, **kwargs):
    bounty = kwargs.pop("bounty")
    super(EditBounty, self).__init__(*args, **kwargs)
    tags = map(lambda t: str(t), bounty.tags.all())
    self.fields["title"].initial = bounty.title
    self.fields["description"].initial = bounty.description
    self.fields["tags"].initial = " ".join(tags)
    self.fields["target"].initial = float(bounty.target_reward)
    self.fields["deadline"].initial = bounty.deadline

class FilterPending(Form):

  searchtext = CharField(
    label=_("SEARCH_TEXT"), 
    required=False,
    widget=TextInput(attrs={
      'class':'form-control', 
      'placeholder' : _('SEARCH_TITLE_AND_TAGS')
    })
  )

  ordering = ChoiceField(
    choices=[
      ('REWARD_HIGHEST', _('REWARD_HIGHEST')),
      ('REWARD_LOWEST', _('REWARD_LOWEST')),
      ('DEADLINE_NEAREST', _('DEADLINE_NEAREST')),
      ('DEADLINE_FARTHEST', _('DEADLINE_FARTHEST')),
      ('NEWEST_BOUNTY', _('NEWEST_BOUNTY')),
      ('OLDEST_BOUNTY', _('OLDEST_BOUNTY')),
    ],
    label=_("ORDERING"),
    initial="REWARD_HIGHEST",
    widget=Select(attrs={'class':'form-control'})
  )

class FilterActive(Form):

  searchtext = CharField(
    label=_("SEARCH_TEXT"), 
    required=False,
    widget=TextInput(attrs={
      'class':'form-control', 
      'placeholder' : _('SEARCH_TITLE_AND_TAGS')
    })
  )

  claims = ChoiceField(
    choices=[
      ('ANY_CLAIMS', _('ANY_CLAIMS')),
      ('NO_CLAIMS', _('NO_CLAIMS')),
      ('HAS_CLAIMS', _('HAS_CLAIMS')),
    ],
    label=_("CLAIMS"),
    initial="ANY_CLAIMS",
    widget=Select(attrs={'class':'form-control'})
  )

  ordering = ChoiceField(
    choices=[
      ('REWARD_HIGHEST', _('REWARD_HIGHEST')),
      ('REWARD_LOWEST', _('REWARD_LOWEST')),
      ('DEADLINE_NEAREST', _('DEADLINE_NEAREST')),
      ('DEADLINE_FARTHEST', _('DEADLINE_FARTHEST')),
      ('NEWEST_BOUNTY', _('NEWEST_BOUNTY')),
      ('OLDEST_BOUNTY', _('OLDEST_BOUNTY')),
    ],
    label=_("ORDERING"),
    initial="REWARD_HIGHEST",
    widget=Select(attrs={'class':'form-control'})
  )

class FilterMediation(Form):

  searchtext = CharField(
    label=_("SEARCH_TEXT"), 
    required=False,
    widget=TextInput(attrs={
      'class':'form-control', 
      'placeholder' : _('SEARCH_TITLE_AND_TAGS')
    })
  )

  ordering = ChoiceField(
    choices=[
      ('REWARD_HIGHEST', _('REWARD_HIGHEST')),
      ('REWARD_LOWEST', _('REWARD_LOWEST')),
      ('DEADLINE_NEAREST', _('DEADLINE_NEAREST')),
      ('DEADLINE_FARTHEST', _('DEADLINE_FARTHEST')),
    ],
    label=_("ORDERING"),
    initial="REWARD_HIGHEST",
    widget=Select(attrs={'class':'form-control'})
  )

class FilterArchived(Form):

  searchtext = CharField(
    label=_("SEARCH_TEXT"), 
    required=False,
    widget=TextInput(attrs={
      'class':'form-control', 
      'placeholder' : _('SEARCH_TITLE_AND_TAGS')
    })
  )

  date_from = DateField(
    label=_("DEADLINE_FROM"),
    required=False,
    widget=DateInput(attrs={
      'class' : 'form-control datepicker', 
      'readonly' : 'true',
      'placeholder' : _('DEADLINE_FROM'),
    }),
  )

  date_to = DateField(
    label=_("DEADLINE_TO"),
    required=False,
    widget=DateInput(attrs={
      'class' : 'form-control datepicker', 
      'readonly' : 'true',
      'placeholder' : _('DEADLINE_TO'),
    }),
  )

  outcome = ChoiceField(
    choices=[
      ('ANY_OUTCOME', _('ANY_OUTCOME')),
      ('REWARDED', _('REWARDED')),
      ('UNREWARDED', _('UNREWARDED')),
      ('CANCELLED', _('CANCELLED')),
    ],
    label=_("OUTCOME"),
    initial="ANY_OUTCOME",
    widget=Select(attrs={'class':'form-control'})
  )

  ordering = ChoiceField(
    choices=[
      ('REWARD_HIGHEST', _('REWARD_HIGHEST')),
      ('REWARD_LOWEST', _('REWARD_LOWEST')),
      ('NEWEST_BOUNTY', _('NEWEST_BOUNTY')),
      ('OLDEST_BOUNTY', _('OLDEST_BOUNTY')),
    ],
    label=_("ORDERING"),
    initial="NEWEST_BOUNTY",
    widget=Select(attrs={'class':'form-control'})
  )

