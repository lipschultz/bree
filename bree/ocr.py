from collections import namedtuple
from typing import Optional

import numpy as np
import pytesseract

from bree.image import Region

OCRMatch = namedtuple('OCRMatch', ['index_start', 'index_end', 'region', 'confidence'])


class OCRMatcher:
    def __init__(self, image_numpy_array: np.ndarray, line_break: str = '\n', paragraph_break: str = '\n\n'):
        self._image = image_numpy_array

        self.line_break_str = line_break
        self.paragraph_break_str = paragraph_break

        self._process_file()

    def _process_file(self):
        df = pytesseract.image_to_data(self._image, output_type=pytesseract.Output.DATAFRAME)
        df = df.dropna()

        final_string = ''
        index_mapping = []
        for _, paragraph in df.groupby(['page_num', 'block_num', 'par_num']):
            if len(final_string) > 0:
                previous_region = index_mapping[-1].region
                index_mapping.append(OCRMatch(
                    len(final_string),
                    len(final_string) + len(self.paragraph_break_str),
                    Region.from_points(previous_region.right, previous_region.top, paragraph.iloc[0]['left'],
                                       previous_region.bottom),
                    None
                ))
                final_string += self.paragraph_break_str

            new_paragraph = True
            for _, line in paragraph.groupby('line_num'):
                if len(final_string) > 0 and not new_paragraph:
                    previous_region = index_mapping[-1].region
                    index_mapping.append(OCRMatch(
                        len(final_string),
                        len(final_string) + len(self.line_break_str),
                        Region.from_points(
                            previous_region.right,
                            previous_region.top,
                            line.iloc[0]['left'],
                            previous_region.bottom
                        ),
                        None
                    ))
                    final_string += self.line_break_str

                new_paragraph = False

                new_line = True
                for _, row in line.iterrows():
                    if row['text'] == '':
                        continue
                    if len(final_string) > 0 and not new_line:
                        previous_region = index_mapping[-1].region
                        index_mapping.append(OCRMatch(
                            len(final_string),
                            len(final_string) + 1,
                            Region.from_points(
                                previous_region.right,
                                previous_region.top,
                                row['left'],
                                previous_region.bottom
                            ),
                            None
                        ))
                        final_string += ' '
                    index_mapping.append(OCRMatch(
                        len(final_string),
                        len(final_string) + len(row['text']),
                        Region(row['left'], row['top'], row['width'], row['height']),
                        row['conf']
                    ))
                    final_string += row['text']
                    new_line = False

        self._parsed_text = final_string
        self._ocr_segments = index_mapping

    @property
    def text(self) -> str:
        return self._parsed_text

    def find(self, needle: str) -> Optional[OCRMatch]:
        index_start = self._parsed_text.find(needle)
        if index_start == -1:
            return None

        index_end = index_start + len(needle)
        for i, token in enumerate(self._ocr_segments):
            if token.index_start <= index_start < token.index_end:
                if index_end <= token.index_end:
                    return token
                tokens = []
                end_token_i = i
                while index_end >= token.index_end:
                    tokens.append(token)
                    end_token_i += 1
                    token = self._ocr_segments[end_token_i]

                return OCRMatch(
                    index_start,
                    index_end,
                    Region.from_points(
                        min(t.region.left for t in tokens),
                        min(t.region.top for t in tokens),
                        max(t.region.right for t in tokens),
                        max(t.region.bottom for t in tokens),
                    ),
                    min(t.confidence for t in tokens if t.confidence is not None)
                )
        return None
