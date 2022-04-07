from pathlib import Path
from unittest.mock import patch, MagicMock

from bree.image import Image
from bree.location import Region
from bree.ocr import OCRMatcher, OCRMatch

RESOURCES_DIR = Path(__file__).parent / 'resources'


WIKI_PYTHON_TEXT_TEXT = (RESOURCES_DIR / 'wiki-python-text.txt').read_text()
WIKI_PYTHON_TEXT_POSITIONS = [
    OCRMatch(0, 6, Region(26, 29, 98, 32), 0.96839996),
    OCRMatch(6, 7, Region(124, 29, 11, 32), None),
    OCRMatch(7, 19, Region(135, 29, 195, 32), 0.96485741),
    OCRMatch(19, 20, Region(330, 29, 10, 32), None),
    OCRMatch(20, 29, Region(340, 29, 133, 32), 0.96132133),
    OCRMatch(29, 31, Region(473, 29, -447, 32), None),
    OCRMatch(31, 32, Region(26, 59, 1287, 21), 0.950),
    OCRMatch(32, 34, Region(1313, 59, -1286, 21), None),
    OCRMatch(34, 38, Region(27, 84, 36, 12), 0.96981003),
    OCRMatch(38, 39, Region(63, 84, 6, 12), None),
    OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
    OCRMatch(49, 50, Region(148, 84, 7, 15), None),
    OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
    OCRMatch(53, 54, Region(179, 84, 6, 12), None),
    OCRMatch(54, 58, Region(185, 84, 30, 12), 0.95936913),
    OCRMatch(58, 59, Region(215, 84, 5, 12), None),
    OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
    OCRMatch(71, 72, Region(321, 84, -271, 15), None),
    OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
    OCRMatch(83, 84, Region(129, 106, 6, 12), None),
    OCRMatch(84, 88, Region(135, 106, 32, 11), 0.96729462),
    OCRMatch(88, 89, Region(167, 106, 7, 11), None),
    OCRMatch(89, 95, Region(174, 106, 47, 14), 0.95819839),
    OCRMatch(95, 96, Region(221, 106, 6, 14), None),
    OCRMatch(96, 108, Region(227, 106, 99, 14), 0.93306213),
    OCRMatch(108, 109, Region(326, 106, 6, 14), None),
    OCRMatch(109, 119, Region(332, 106, 79, 14), 0.9209182),
    OCRMatch(119, 121, Region(411, 106, -384, 14), None),
    OCRMatch(121, 127, Region(27, 145, 65, 18), 0.96068909),
    OCRMatch(127, 128, Region(92, 145, 8, 18), None),
    OCRMatch(128, 130, Region(100, 145, 11, 14), 0.92610542),
    OCRMatch(130, 131, Region(111, 145, 7, 14), None),
    OCRMatch(131, 132, Region(118, 149, 8, 10), 0.92610542),
    OCRMatch(132, 133, Region(126, 149, 8, 10), None),
    OCRMatch(133, 144, Region(134, 145, 86, 18), 0.95575119),
    OCRMatch(144, 145, Region(220, 145, 7, 18), None),
    OCRMatch(145, 160, Region(227, 145, 137, 18), 0.9659726),
    OCRMatch(160, 161, Region(364, 145, 7, 18), None),
    OCRMatch(161, 172, Region(371, 145, 112, 18), 0.96498505),
    OCRMatch(172, 173, Region(483, 145, 8, 18), None),
    OCRMatch(173, 182, Region(491, 145, 80, 18), 0.96685806),
    OCRMatch(182, 183, Region(571, 145, 8, 18), None),
    OCRMatch(183, 186, Region(579, 146, 19, 13), 0.95782547),
    OCRMatch(186, 187, Region(598, 146, 6, 13), None),
    OCRMatch(187, 193, Region(604, 145, 54, 18), 0.96983559),
    OCRMatch(193, 194, Region(658, 145, 8, 18), None),
    OCRMatch(194, 204, Region(666, 145, 89, 18), 0.96196815),
    OCRMatch(204, 205, Region(755, 145, 7, 18), None),
    OCRMatch(205, 215, Region(762, 145, 98, 18), 0.96613731),
    OCRMatch(215, 216, Region(860, 145, 7, 18), None),
    OCRMatch(216, 220, Region(867, 145, 39, 14), 0.96990463),
    OCRMatch(220, 221, Region(906, 145, 7, 14), None),
    OCRMatch(221, 232, Region(913, 145, 88, 18), 0.96296272),
    OCRMatch(232, 233, Region(1001, 145, 6, 18), None),
    OCRMatch(233, 237, Region(1007, 145, 34, 14), 0.96296272),
    OCRMatch(237, 238, Region(1041, 145, 7, 14), None),
    OCRMatch(238, 241, Region(1048, 145, 27, 14), 0.97011108),
    OCRMatch(241, 242, Region(1075, 145, 6, 14), None),
    OCRMatch(242, 245, Region(1081, 149, 29, 10), 0.96997353),
    OCRMatch(245, 246, Region(1110, 149, 6, 10), None),
    OCRMatch(246, 248, Region(1116, 145, 16, 14), 0.969188),
    OCRMatch(248, 249, Region(1132, 145, 6, 14), None),
    OCRMatch(249, 260, Region(1138, 145, 86, 18), 0.969188),
    OCRMatch(260, 262, Region(1224, 145, -1196, 18), None),
    OCRMatch(262, 274, Region(28, 172, 98, 14), 0.96875984),
    OCRMatch(274, 275, Region(126, 172, 8, 14), None),
    OCRMatch(275, 278, Region(134, 173, 19, 13), 0.9559507),
    OCRMatch(278, 279, Region(153, 173, 7, 13), None),
    OCRMatch(279, 287, Region(160, 172, 76, 18), 0.96281914),
    OCRMatch(287, 288, Region(236, 172, 7, 18), None),
    OCRMatch(288, 298, Region(243, 173, 86, 13), 0.96975685),
    OCRMatch(298, 299, Region(329, 173, 6, 13), None),
    OCRMatch(299, 302, Region(335, 172, 30, 14), 0.97000175),
    OCRMatch(302, 303, Region(365, 172, 8, 14), None),
    OCRMatch(303, 318, Region(373, 172, 126, 18), 0.96658142),
    OCRMatch(318, 319, Region(499, 172, 7, 18), None),
    OCRMatch(319, 327, Region(506, 172, 77, 18), 0.96751053),
    OCRMatch(327, 328, Region(583, 172, 7, 18), None),
    OCRMatch(328, 331, Region(590, 172, 30, 14), 0.96905067),
    OCRMatch(331, 332, Region(620, 172, 6, 14), None),
    OCRMatch(332, 334, Region(626, 173, 16, 13), 0.96767982),
    OCRMatch(334, 335, Region(642, 173, 8, 13), None),
    OCRMatch(335, 339, Region(650, 172, 34, 18), 0.96535873),
    OCRMatch(339, 340, Region(684, 172, 7, 18), None),
    OCRMatch(340, 351, Region(691, 176, 113, 14), 0.96542938),
    OCRMatch(351, 352, Region(804, 176, 6, 14), None),
    OCRMatch(352, 357, Region(810, 172, 41, 14), 0.96979988),
    OCRMatch(357, 358, Region(851, 172, 7, 14), None),
    OCRMatch(358, 364, Region(858, 172, 45, 16), 0.96815186),
    OCRMatch(364, 365, Region(903, 172, 7, 16), None),
    OCRMatch(365, 372, Region(910, 172, 53, 18), 0.96903061),
    OCRMatch(372, 373, Region(963, 172, 7, 18), None),
    OCRMatch(373, 377, Region(970, 172, 39, 14), 0.96522537),
    OCRMatch(377, 378, Region(1009, 172, 6, 14), None),
    OCRMatch(378, 381, Region(1015, 172, 23, 14), 0.93267509),
    OCRMatch(381, 382, Region(1038, 172, 6, 14), None),
    OCRMatch(382, 388, Region(1044, 172, 50, 14), 0.92484375),
    OCRMatch(388, 389, Region(1094, 172, 6, 14), None),
    OCRMatch(389, 392, Region(1100, 172, 30, 14), 0.96983086),
    OCRMatch(392, 393, Region(1130, 172, 7, 14), None),
    OCRMatch(393, 404, Region(1137, 172, 91, 18), 0.96914345),
    OCRMatch(404, 405, Region(1228, 172, -1201, 18), None),
    OCRMatch(405, 418, Region(27, 196, 98, 21), 0.90860062),
    OCRMatch(418, 420, Region(125, 196, -98, 21), None),
    OCRMatch(420, 426, Region(27, 234, 56, 18), 0.96858826),
    OCRMatch(426, 427, Region(83, 234, 8, 18), None),
    OCRMatch(427, 429, Region(91, 234, 12, 14), 0.93286751),
    OCRMatch(429, 430, Region(103, 234, 6, 14), None),
    OCRMatch(430, 447, Region(109, 234, 154, 18), 0.92509521),
    OCRMatch(447, 448, Region(263, 234, 7, 18), None),
    OCRMatch(448, 451, Region(270, 234, 30, 14), 0.9323365),
    OCRMatch(451, 452, Region(300, 234, 7, 14), None),
    OCRMatch(452, 470, Region(307, 234, 155, 18), 0.92570442),
    OCRMatch(470, 471, Region(462, 234, 8, 18), None),
    OCRMatch(471, 473, Region(470, 235, 10, 13), 0.95902161),
    OCRMatch(473, 474, Region(480, 235, 6, 13), None),
    OCRMatch(474, 482, Region(486, 235, 72, 17), 0.9686689),
    OCRMatch(482, 483, Region(558, 235, 7, 17), None),
    OCRMatch(483, 491, Region(565, 234, 67, 18), 0.96991539),
    OCRMatch(491, 492, Region(632, 234, 7, 18), None),
    OCRMatch(492, 503, Region(639, 234, 112, 18), 0.96328499),
    OCRMatch(503, 504, Region(751, 234, 8, 18), None),
    OCRMatch(504, 514, Region(759, 234, 92, 18), 0.96699387),
    OCRMatch(514, 515, Region(851, 234, 7, 18), None),
    OCRMatch(515, 524, Region(858, 234, 75, 18), 0.96904434),
    OCRMatch(524, 525, Region(933, 234, 7, 18), None),
    OCRMatch(525, 535, Region(940, 234, 85, 14), 0.96694527),
    OCRMatch(535, 536, Region(1025, 234, 7, 14), None),
    OCRMatch(536, 549, Region(1032, 234, 101, 18), 0.96691345),
    OCRMatch(549, 550, Region(1133, 234, 7, 18), None),
    OCRMatch(550, 562, Region(1140, 234, 99, 18), 0.93301041),
    OCRMatch(562, 563, Region(1239, 234, 8, 18), None),
    OCRMatch(563, 570, Region(1247, 234, 56, 18), 0.93091675),
    OCRMatch(570, 571, Region(1303, 234, -1276, 18), None),
    OCRMatch(571, 579, Region(27, 261, 68, 14), 0.96471481),
    OCRMatch(579, 580, Region(95, 261, 7, 14), None),
    OCRMatch(580, 583, Region(102, 261, 30, 14), 0.96960045),
    OCRMatch(583, 584, Region(132, 261, 7, 14), None),
    OCRMatch(584, 594, Region(139, 261, 82, 14), 0.96931328),
    OCRMatch(594, 595, Region(221, 261, 8, 14), None),
    OCRMatch(595, 607, Region(229, 261, 116, 18), 0.96407089),
    OCRMatch(607, 608, Region(345, 261, 8, 18), None),
    OCRMatch(608, 610, Region(353, 262, 11, 13), 0.96754875),
    OCRMatch(610, 611, Region(364, 262, 6, 13), None),
    OCRMatch(611, 613, Region(370, 261, 12, 14), 0.96933273),
    OCRMatch(613, 614, Region(382, 261, 7, 14), None),
    OCRMatch(614, 619, Region(389, 261, 41, 14), 0.96205933),
    OCRMatch(619, 620, Region(430, 261, 7, 14), None),
    OCRMatch(620, 629, Region(437, 261, 81, 14), 0.96314354),
    OCRMatch(629, 630, Region(518, 261, 7, 14), None),
    OCRMatch(630, 632, Region(525, 265, 18, 10), 0.96154991),
    OCRMatch(632, 633, Region(543, 265, 6, 10), None),
    OCRMatch(633, 634, Region(549, 265, 9, 10), 0.92193237),
    OCRMatch(634, 635, Region(558, 265, 7, 10), None),
    OCRMatch(635, 645, Region(565, 261, 82, 14), 0.92193237),
    OCRMatch(645, 646, Region(647, 261, 7, 14), None),
    OCRMatch(646, 655, Region(654, 261, 77, 14), 0.95749687),
    OCRMatch(655, 656, Region(731, 261, 7, 14), None),
    OCRMatch(656, 664, Region(738, 261, 77, 18), 0.9666507),
    OCRMatch(664, 665, Region(815, 261, 6, 18), None),
    OCRMatch(665, 668, Region(821, 261, 31, 14), 0.96912888),
    OCRMatch(668, 669, Region(852, 261, 6, 14), None),
    OCRMatch(669, 671, Region(858, 262, 16, 13), 0.96912888),
    OCRMatch(671, 672, Region(874, 262, 7, 13), None),
    OCRMatch(672, 675, Region(881, 261, 18, 14), 0.96961411),
    OCRMatch(675, 676, Region(899, 261, 7, 14), None),
    OCRMatch(676, 689, Region(906, 261, 127, 18), 0.9690255),
    OCRMatch(689, 690, Region(1033, 261, 7, 18), None),
    OCRMatch(690, 698, Region(1040, 261, 73, 14), 0.93268143),
    OCRMatch(698, 699, Region(1113, 261, 8, 14), None),
    OCRMatch(699, 715, Region(1121, 258, 110, 21), 0.11985886),
    OCRMatch(715, 717, Region(1231, 258, -1204, 21), None),
    OCRMatch(717, 722, Region(27, 296, 48, 14), 0.96630913),
    OCRMatch(722, 723, Region(75, 296, 6, 14), None),
    OCRMatch(723, 726, Region(81, 300, 29, 10), 0.96557976),
    OCRMatch(726, 727, Region(110, 300, 8, 10), None),
    OCRMatch(727, 733, Region(118, 297, 64, 13), 0.95687012),
    OCRMatch(733, 734, Region(182, 297, 7, 13), None),
    OCRMatch(734, 739, Region(189, 296, 50, 18), 0.95687012),
    OCRMatch(739, 740, Region(239, 296, 7, 18), None),
    OCRMatch(740, 747, Region(246, 296, 65, 18), 0.96586197),
    OCRMatch(747, 748, Region(311, 296, 7, 18), None),
    OCRMatch(748, 750, Region(318, 300, 20, 10), 0.96718559),
    OCRMatch(750, 751, Region(338, 300, 7, 10), None),
    OCRMatch(751, 757, Region(345, 296, 56, 18), 0.9649192),
    OCRMatch(757, 758, Region(401, 296, 8, 18), None),
    OCRMatch(758, 760, Region(409, 296, 13, 14), 0.9686763),
    OCRMatch(760, 761, Region(422, 296, 6, 14), None),
    OCRMatch(761, 764, Region(428, 296, 27, 14), 0.96328171),
    OCRMatch(764, 765, Region(455, 296, 7, 14), None),
    OCRMatch(765, 769, Region(462, 296, 31, 14), 0.96613899),
    OCRMatch(769, 770, Region(493, 296, 7, 14), None),
    OCRMatch(770, 775, Region(500, 297, 49, 13), 0.96613899),
    OCRMatch(775, 776, Region(549, 297, 7, 13), None),
    OCRMatch(776, 778, Region(556, 300, 18, 10), 0.95859673),
    OCRMatch(778, 779, Region(574, 300, 6, 10), None),
    OCRMatch(779, 780, Region(580, 300, 9, 10), 0.95859673),
    OCRMatch(780, 781, Region(589, 300, 7, 10), None),
    OCRMatch(781, 790, Region(596, 300, 83, 10), 0.96675064),
    OCRMatch(790, 791, Region(679, 300, 5, 10), None),
    OCRMatch(791, 793, Region(684, 297, 16, 13), 0.96623848),
    OCRMatch(793, 794, Region(700, 297, 6, 13), None),
    OCRMatch(794, 797, Region(706, 296, 27, 14), 0.96533272),
    OCRMatch(797, 798, Region(733, 296, 6, 14), None),
    OCRMatch(798, 801, Region(739, 297, 33, 13), 0.97008179),
    OCRMatch(801, 802, Region(772, 297, 8, 13), None),
    OCRMatch(802, 813, Region(780, 296, 111, 18), 0.95698425),
    OCRMatch(813, 814, Region(891, 296, 8, 18), None),
    OCRMatch(814, 822, Region(899, 296, 76, 18), 0.96569885),
    OCRMatch(822, 823, Region(975, 296, 7, 18), None),
    OCRMatch(823, 826, Region(982, 296, 30, 14), 0.9601339),
    OCRMatch(826, 827, Region(1012, 296, 6, 14), None),
    OCRMatch(827, 832, Region(1018, 296, 33, 14), 0.94546799),
    OCRMatch(832, 833, Region(1051, 296, 6, 14), None),
    OCRMatch(833, 841, Region(1057, 296, 70, 14), 0.94546799),
    OCRMatch(841, 842, Region(1127, 296, 8, 14), None),
    OCRMatch(842, 844, Region(1135, 296, 10, 14), 0.95946083),
    OCRMatch(844, 845, Region(1145, 296, 6, 14), None),
    OCRMatch(845, 847, Region(1151, 296, 13, 14), 0.95946083),
    OCRMatch(847, 848, Region(1164, 296, 8, 14), None),
    OCRMatch(848, 852, Region(1172, 297, 40, 13), 0.95981712),
    OCRMatch(852, 853, Region(1212, 297, 8, 13), None),
    OCRMatch(853, 855, Region(1220, 300, 18, 10), 0.96540657),
    OCRMatch(855, 856, Region(1238, 300, -1211, 10), None),
    OCRMatch(856, 862, Region(27, 323, 56, 18), 0.93303421),
    OCRMatch(862, 863, Region(83, 323, 7, 18), None),
    OCRMatch(863, 873, Region(90, 321, 75, 16), 0.4475782),
    OCRMatch(873, 874, Region(165, 321, 7, 16), None),
    OCRMatch(874, 880, Region(172, 323, 56, 18), 0.95388069),
    OCRMatch(880, 881, Region(228, 323, 7, 18), None),
    OCRMatch(881, 884, Region(235, 324, 25, 13), 0.96271393),
    OCRMatch(884, 885, Region(260, 324, 6, 13), None),
    OCRMatch(885, 888, Region(266, 327, 32, 10), 0.9685984),
    OCRMatch(888, 889, Region(298, 327, 7, 10), None),
    OCRMatch(889, 897, Region(305, 323, 70, 14), 0.9642614),
    OCRMatch(897, 898, Region(375, 323, 8, 14), None),
    OCRMatch(898, 900, Region(383, 323, 13, 14), 0.96971771),
    OCRMatch(900, 901, Region(396, 323, 7, 14), None),
    OCRMatch(901, 905, Region(403, 324, 41, 13), 0.96908661),
    OCRMatch(905, 906, Region(444, 324, 7, 13), None),
    OCRMatch(906, 909, Region(451, 323, 30, 14), 0.96532547),
    OCRMatch(909, 910, Region(481, 323, 7, 14), None),
    OCRMatch(910, 920, Region(488, 323, 88, 14), 0.96308678),
    OCRMatch(920, 921, Region(576, 323, 8, 14), None),
    OCRMatch(921, 924, Region(584, 327, 33, 10), 0.96594292),
    OCRMatch(924, 925, Region(617, 327, 6, 10), None),
    OCRMatch(925, 933, Region(623, 323, 69, 14), 0.96826683),
    OCRMatch(933, 934, Region(692, 323, 6, 14), None),
    OCRMatch(934, 938, Region(698, 323, 38, 14), 0.96826683),
    OCRMatch(938, 939, Region(736, 323, 7, 14), None),
    OCRMatch(939, 941, Region(743, 327, 18, 10), 0.9683519),
    OCRMatch(941, 942, Region(761, 327, 7, 10), None),
    OCRMatch(942, 946, Region(768, 323, 23, 14), 0.93268127),
    OCRMatch(946, 947, Region(791, 323, 6, 14), None),
    OCRMatch(947, 962, Region(797, 323, 142, 18), 0.90784012),
    OCRMatch(962, 963, Region(939, 323, 7, 18), None),
    OCRMatch(963, 978, Region(946, 323, 128, 18), 0.91932976),
    OCRMatch(978, 979, Region(1074, 323, 7, 18), None),
    OCRMatch(979, 986, Region(1081, 323, 68, 18), 0.96831558),
    OCRMatch(986, 987, Region(1149, 323, 7, 18), None),
    OCRMatch(987, 998, Region(1156, 323, 84, 16), 0.96971077),
    OCRMatch(998, 1000, Region(1240, 323, -1213, 16), None),
    OCRMatch(1000, 1009, Region(27, 350, 79, 14), 0.95473503),
    OCRMatch(1009, 1010, Region(106, 350, 6, 14), None),
    OCRMatch(1010, 1019, Region(112, 350, 77, 18), 0.96591553),
    OCRMatch(1019, 1020, Region(189, 350, 7, 18), None),
    OCRMatch(1020, 1023, Region(196, 350, 30, 14), 0.96999527),
    OCRMatch(1023, 1024, Region(226, 350, 8, 14), None),
    OCRMatch(1024, 1031, Region(234, 350, 66, 14), 0.96728638),
    OCRMatch(1031, 1032, Region(300, 350, 6, 14), None),
    OCRMatch(1032, 1040, Region(306, 351, 68, 17), 0.96908432),
    OCRMatch(1040, 1041, Region(374, 351, 8, 17), None),
    OCRMatch(1041, 1047, Region(382, 350, 56, 18), 0.96937523),
    OCRMatch(1047, 1048, Region(438, 350, 8, 18), None),
    OCRMatch(1048, 1052, Region(446, 351, 30, 15), 0.96646156),
    OCRMatch(1052, 1053, Region(476, 351, 7, 15), None),
    OCRMatch(1053, 1061, Region(483, 350, 70, 14), 0.96646156),
    OCRMatch(1061, 1062, Region(553, 350, 7, 14), None),
    OCRMatch(1062, 1064, Region(560, 350, 14, 14), 0.96396957),
    OCRMatch(1064, 1065, Region(574, 350, 7, 14), None),
    OCRMatch(1065, 1070, Region(581, 351, 46, 15), 0.96772591),
    OCRMatch(1070, 1071, Region(627, 351, 7, 15), None),
    OCRMatch(1071, 1074, Region(634, 354, 32, 10), 0.96939651),
    OCRMatch(1074, 1075, Region(666, 354, 6, 10), None),
    OCRMatch(1075, 1076, Region(672, 354, 9, 10), 0.96939651),
    OCRMatch(1076, 1077, Region(681, 354, 7, 10), None),
    OCRMatch(1077, 1082, Region(688, 350, 48, 18), 0.96703964),
    OCRMatch(1082, 1083, Region(736, 350, 6, 18), None),
    OCRMatch(1083, 1091, Region(742, 350, 64, 14), 0.96614616),
    OCRMatch(1091, 1092, Region(806, 350, 6, 14), None),
    OCRMatch(1092, 1096, Region(812, 350, 34, 14), 0.96614616),
    OCRMatch(1096, 1097, Region(846, 350, 7, 14), None),
    OCRMatch(1097, 1099, Region(853, 350, 12, 14), 0.96939667),
    OCRMatch(1099, 1100, Region(865, 350, 7, 14), None),
    OCRMatch(1100, 1103, Region(872, 351, 26, 13), 0.96971817),
    OCRMatch(1103, 1104, Region(898, 351, 6, 13), None),
    OCRMatch(1104, 1114, Region(904, 350, 92, 18), 0.93306206),
    OCRMatch(1114, 1115, Region(996, 350, 7, 18), None),
    OCRMatch(1115, 1134, Region(1003, 350, 179, 18), 0.91678215),
    OCRMatch(1134, 1135, Region(1182, 350, 6, 18), None),
    OCRMatch(1135, 1139, Region(1188, 350, 35, 14), 0.96943748),
    OCRMatch(1139, 1140, Region(1223, 350, 7, 14), None),
    OCRMatch(1140, 1147, Region(1230, 350, 54, 14), 0.96815567),
    OCRMatch(1147, 1148, Region(1284, 350, -1258, 14), None),
    OCRMatch(1148, 1157, Region(26, 377, 74, 14), 0.96771805),
    OCRMatch(1157, 1158, Region(100, 377, 8, 14), None),
    OCRMatch(1158, 1164, Region(108, 377, 56, 18), 0.96986267),
    OCRMatch(1164, 1165, Region(164, 377, 7, 18), None),
    OCRMatch(1165, 1166, Region(171, 378, 9, 13), 0.96986267),
    OCRMatch(1166, 1167, Region(180, 378, 7, 13), None),
    OCRMatch(1167, 1170, Region(187, 381, 32, 10), 0.96959419),
    OCRMatch(1170, 1171, Region(219, 381, 6, 10), None),
    OCRMatch(1171, 1183, Region(225, 377, 106, 14), 0.9689682),
    OCRMatch(1183, 1184, Region(331, 377, 7, 14), None),
    OCRMatch(1184, 1188, Region(338, 377, 34, 14), 0.96747581),
    OCRMatch(1188, 1189, Region(372, 377, 7, 14), None),
    OCRMatch(1189, 1196, Region(379, 377, 60, 14), 0.97006226),
    OCRMatch(1196, 1197, Region(439, 377, 7, 14), None),
    OCRMatch(1197, 1203, Region(446, 378, 52, 13), 0.96959641),
    OCRMatch(1203, 1204, Region(498, 378, 7, 13), None),
    OCRMatch(1204, 1206, Region(505, 377, 14, 14), 0.93026123),
    OCRMatch(1206, 1207, Region(519, 377, 7, 14), None),
    OCRMatch(1207, 1216, Region(526, 374, 74, 17), 0.06733658),
    OCRMatch(1216, 1218, Region(600, 374, -573, 17), None),
    OCRMatch(1218, 1224, Region(27, 412, 56, 18), 0.96732483),
    OCRMatch(1224, 1225, Region(83, 412, 7, 18), None),
    OCRMatch(1225, 1237, Region(90, 412, 100, 18), 0.96689476),
    OCRMatch(1237, 1238, Region(190, 412, 7, 18), None),
    OCRMatch(1238, 1243, Region(197, 412, 45, 14), 0.96689476),
    OCRMatch(1243, 1244, Region(242, 412, 6, 14), None),
    OCRMatch(1244, 1246, Region(248, 416, 18, 10), 0.96805046),
    OCRMatch(1246, 1247, Region(266, 416, 7, 10), None),
    OCRMatch(1247, 1250, Region(273, 416, 30, 10), 0.95946228),
    OCRMatch(1250, 1251, Region(303, 416, 6, 10), None),
    OCRMatch(1251, 1253, Region(309, 412, 17, 14), 0.96807182),
    OCRMatch(1253, 1254, Region(326, 412, 4, 14), None),
    OCRMatch(1254, 1257, Region(330, 412, 27, 14), 0.96940147),
    OCRMatch(1257, 1258, Region(357, 412, 7, 14), None),
    OCRMatch(1258, 1262, Region(364, 413, 41, 13), 0.96858246),
    OCRMatch(1262, 1263, Region(405, 413, 7, 13), None),
    OCRMatch(1263, 1270, Region(412, 412, 63, 18), 0.96858246),
    OCRMatch(1270, 1271, Region(475, 412, 6, 18), None),
    OCRMatch(1271, 1282, Region(481, 412, 112, 18), 0.96070175),
    OCRMatch(1282, 1283, Region(593, 412, 7, 18), None),
    OCRMatch(1283, 1293, Region(600, 406, 86, 29), 0.01359695),
    OCRMatch(1293, 1294, Region(686, 406, 6, 29), None),
    OCRMatch(1294, 1310, Region(692, 410, 109, 16), 0.01359695),
    OCRMatch(1310, 1311, Region(801, 410, -774, 16), None),
    OCRMatch(1311, 1322, Region(27, 445, 106, 15), 0.96406143),
    OCRMatch(1322, 1323, Region(133, 445, 7, 15), None),
    OCRMatch(1323, 1333, Region(140, 445, 86, 15), 0.96406143),
    OCRMatch(1333, 1335, Region(226, 445, -200, 15), None),
    OCRMatch(1335, 1336, Region(26, 468, 11, 33), 0.0),
    OCRMatch(1336, 1337, Region(37, 468, 15, 33), None),
    OCRMatch(1337, 1343, Region(52, 479, 57, 17), 0.96549629),
    OCRMatch(1343, 1345, Region(109, 479, -79, 17), None),
    OCRMatch(1345, 1347, Region(30, 500, 14, 14), 0.05199097),
    OCRMatch(1347, 1348, Region(44, 500, 8, 14), None),
    OCRMatch(1348, 1352, Region(52, 499, 42, 17), 0.95932671),
    OCRMatch(1352, 1354, Region(94, 499, -64, 17), None),
    OCRMatch(1354, 1355, Region(30, 520, 14, 14), 0.84948273),
    OCRMatch(1355, 1356, Region(44, 520, 6, 14), None),
    OCRMatch(1356, 1360, Region(50, 520, 37, 16), 0.94611794),
    OCRMatch(1360, 1361, Region(87, 520, -61, 16), None),
    OCRMatch(1361, 1362, Region(26, 530, 11, 32), 0.13477058),
    OCRMatch(1362, 1363, Region(37, 530, 13, 32), None),
    OCRMatch(1363, 1373, Region(50, 540, 83, 16), 0.96747063)
]


def assert_ocr_match_equal(match1, match2, confidence_tolerance=1e-8):
    assert isinstance(match1, OCRMatch)
    assert isinstance(match2, OCRMatch)
    assert match1.index_start == match2.index_start
    assert match1.index_end == match2.index_end
    assert match1.region == match2.region

    assert (match1.confidence is None and match2.confidence is None) \
           or abs(match1.confidence - match2.confidence) < confidence_tolerance


class TestOCRMatcher:
    @staticmethod
    def test_loading_image_with_text():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')

        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.text == WIKI_PYTHON_TEXT_TEXT
        for i, (actual, expected) in enumerate(zip(matcher._ocr_segments, WIKI_PYTHON_TEXT_POSITIONS)):
            assert_ocr_match_equal(actual, expected)


class TestFindingBoundingBoxes:
    @staticmethod
    def test_finding_complete_single_word():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            expected = (50, 53, [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)])
            assert matcher.find_bounding_boxes('the') == expected

    @staticmethod
    def test_finding_complete_single_word_using_regex():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            expected = (50, 53, [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)])
            assert matcher.find_bounding_boxes('the', regex=True) == expected

    @staticmethod
    def test_finding_complete_single_word_with_start_offset():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            expected = (50, 53, [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)])
            assert matcher.find_bounding_boxes('the', start=20) == expected

    @staticmethod
    def test_finding_complete_single_word_using_regex_with_start_offset():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            expected = (50, 53, [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)])
            assert matcher.find_bounding_boxes('the', start=20, regex=True) == expected

    @staticmethod
    def test_finding_latter_part_of_single_word_finds_entire_words_bounding_box():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('he') == (51, 53, [
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)
            ])

    @staticmethod
    def test_finding_beginning_part_of_single_word_finds_entire_words_bounding_box():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            expected = (72, 76, [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)])
            assert matcher.find_bounding_boxes('(Red') == expected

    @staticmethod
    def test_finding_complete_single_word_with_preceding_space():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes(' the') == (49, 53, [
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
            ])

    @staticmethod
    def test_finding_complete_single_word_with_space_before_and_after():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes(' the ') == (49, 54, [
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                OCRMatch(53, 54, Region(179, 84, 6, 12), None),
            ])

    @staticmethod
    def test_finding_two_words():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('Wikipedia, the') == (39, 53, [
                OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
            ])

    @staticmethod
    def test_finding_complete_single_word_on_second_line():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('(Redirected') == (72, 83, [
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)
            ])

    @staticmethod
    def test_specifying_end_before_token_found_fails_to_find_token():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('(Redirected', end=50) == (-1, -1, [])

    @staticmethod
    def test_specifying_end_before_token_found_fails_to_find_token_using_regex():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('(Redirected', end=50) == (-1, -1, [])

    @staticmethod
    def test_finding_two_words_on_separate_lines():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('encyclopedia\n(Redirected') == (59, 83, [
                OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)
            ])

    @staticmethod
    def test_finding_needle_with_regex_pattern():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes(r'encyclopedia\s+\(Redirected', regex=True) == (59, 83, [
                OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)
            ])

    @staticmethod
    def test_failing_to_find_needle():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('NOT IN TEXT') == (-1, -1, [])

    @staticmethod
    def test_failing_to_find_needle_using_regex():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('NOT IN TEXT', regex=True) == (-1, -1, [])

    @staticmethod
    def test_specifying_start_after_token_found_fails_to_find_token():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('Wikipedia', start=100) == (-1, -1, [])

    @staticmethod
    def test_specifying_start_after_token_found_fails_to_find_token_using_regex():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS

            assert matcher.find_bounding_boxes('Wikipedia', start=100, regex=True) == (-1, -1, [])

    @staticmethod
    def test_finding_all_when_there_are_no_results_returns_empty_list():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(-1, -1, []))

            assert matcher.find_bounding_boxes_all('NOT IN TEXT') == []

    @staticmethod
    def test_finding_all_when_there_is_one_result_returns_list_with_one_result():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(side_effect=[
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)]),
                (-1, -1, []),
            ])

            assert matcher.find_bounding_boxes_all('Wikipedia') == [
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)]),
            ]

    @staticmethod
    def test_finding_all_when_there_is_one_result_but_multiple_boxes_returns_list_with_one_result():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(side_effect=[
                (39, 53, [
                    OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                    OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                    OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                ]),
                (-1, -1, []),
            ])

            assert matcher.find_bounding_boxes_all('Wikipedia') == [
                (39, 53, [
                    OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                    OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                    OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                ]),
            ]

    @staticmethod
    def test_finding_all_when_there_are_many_results():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(side_effect=[
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 90)]),
                (72, 83, [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)]),
                (-1, -1, []),
            ])

            assert matcher.find_bounding_boxes_all('Wikipedia') == [
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 90)]),
                (72, 83, [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)]),
            ]


class TestFind:
    @staticmethod
    def test_failing_to_find_needle():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = WIKI_PYTHON_TEXT_TEXT
            matcher._ocr_segments = WIKI_PYTHON_TEXT_POSITIONS
            matcher.find_bounding_boxes = MagicMock(return_value=(-1, -1, []))

            assert matcher.find('NOT IN TEXT') is None
            matcher.find_bounding_boxes.assert_called_once_with('NOT IN TEXT', None, None, False, 0)

    @staticmethod
    def test_finding_one_bounding_box_where_indices_match_text_result_indices():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(1, 8, [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)
            ]))

            assert matcher.find('IN TEXT') == OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)

    @staticmethod
    def test_finding_one_bounding_box_where_indices_dont_match_text_result_indices():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(3, 7, [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)
            ]))

            assert matcher.find('N TEX') == OCRMatch(3, 7, Region(155, 84, 24, 12), 0.90)

    @staticmethod
    def test_finding_bounding_boxes_on_same_line():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(39, 53, [
                OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
            ]))

            assert matcher.find('Wikipedia, the') == OCRMatch(39, 53, Region(69, 84, 110, 15), 0.94515457)

    @staticmethod
    def test_finding_bounding_boxes_across_lines():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(59, 83, [
                OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)
            ]))

            assert matcher.find('encyclopedia\n(Redirected') == OCRMatch(59, 83, Region(50, 84, 271, 34), 0.96515205)

    @staticmethod
    def test_finding_all_when_there_are_no_results_returns_empty_list():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(return_value=None)

            assert matcher.find_all('NOT IN TEXT') == []

    @staticmethod
    def test_finding_all_when_there_is_one_result_returns_list_with_one_result():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(side_effect=[
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                None,
            ])

            assert matcher.find_all('Wikipedia') == [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
            ]

    @staticmethod
    def test_finding_all_when_there_are_many_results():
        with patch('bree.ocr.OCRMatcher._process_file'):
            any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(side_effect=[
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
                None,
            ])

            assert matcher.find_all('Wikipedia') == [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
            ]
