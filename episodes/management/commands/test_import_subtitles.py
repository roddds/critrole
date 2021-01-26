from .import_subtitles import Command as ImportSubtitles

def test_get_speakers():
  importsub = ImportSubtitles()

  assert importsub.get_speakers('SAM') == ['SAM']
  assert importsub.get_speakers('SAM (V.O.)') == ['SAM']
  assert importsub.get_speakers('TALIESIN and MARISHA') == ['TALIESIN', 'MARISHA']
  assert importsub.get_speakers('SAM, LAURA, and MATTHEW') == ['SAM', 'LAURA', 'MATTHEW']
  assert importsub.get_speakers('LIAM, LAURA, MATTHEW, and ASHLEY') == ['LIAM', 'LAURA', 'MATTHEW', 'ASHLEY']
  assert importsub.get_speakers('LIAM, LAURA, MATTHEW and ASHLEY (V.O.)') == ['LIAM', 'LAURA', 'MATTHEW', 'ASHLEY']
  assert importsub.get_speakers('LIAM, LAURA, MATTHEW and ASHLEY') == ['LIAM', 'LAURA', 'MATTHEW', 'ASHLEY']
  assert importsub.get_speakers('SCARY VOICE OVER') == ['SCARY VOICE OVER']
  assert importsub.get_speakers('SCARY VOICE OVER, SAM') == ['SCARY VOICE OVER', 'SAM']
