/**
 * 游戏资源文件 - AI生成的图片资源
 */

/** 角色立绘图片 */
export const CHARACTER_ILLUSTRATIONS = {
  'zhuge-liang':
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_35b2c063-7550-4fe2-b9bd-cf09b2b2a0c3.jpeg?sign=1805254024-7e865c6edf-0-e1d4d76a455635ed8a2a94af0a4ff68f1e6c568ad57b281eaa41f605236e87ad',
  napoleon:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_747c84ea-4ce4-4fda-976e-38cffbe88ff6.jpeg?sign=1805254025-070ea864f0-0-49d46606c411a97a69214230e7a5a9f2b1c334a565753551b9615ca567902b94',
  arthur:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_4b735d43-561d-4c24-8383-b0bb4427d1de.jpeg?sign=1805254025-4991ceed33-0-34ccc0980662e3e24c6f0c3c1e8c4ca26282662fa5be4fb760624227e3b856a1',
  'wu-zetian':
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_73659947-6869-4056-9210-7fc1870e6965.jpeg?sign=1805254026-46227b271c-0-db6fa75a59e8fc59c23d26f16a57720d3aa72cabd209e6f9705c4eaddc32b35b',
  'hua-mulan':
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_05221975-dcd2-435f-a72a-36ec67270ef7.jpeg?sign=1805254024-87eea505ef-0-6dfc749a579cf2979d8b020d28c72612b71fd9b7899480cf859bee35a10d5942',
  caesar:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_b7d7fd75-6bc6-4324-b4b0-e596ff520de1.jpeg?sign=1805254025-2abc2e29d2-0-652a501bf0b6c99023f1c22f122261e9f512ab691e06d8a027a15bab944871c5',
} as const;

/** 技能特效图片 */
export const SKILL_EFFECTS = {
  light:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_6df8357a-8c73-4300-9f01-f34535f0a5a1.jpeg?sign=1805254054-9374e32287-0-759708c0238544a53ec8b801ad0cdb7af545095c267b3a3f0f623fb0433f9fbb',
  fire:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_2106cdd8-30a8-4cb6-9e16-a35899690d27.jpeg?sign=1805254058-c6f05cd47b-0-e21892ff077571b3db52331755033bfac3452fc1f7f4d0f60b06e23afaacfbc8',
  dark:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_d92881df-2d8f-472b-a753-12263efe08c5.jpeg?sign=1805254057-b284d98907-0-0a85c85628364bf65d47db7527189bcb14d82547d7897fecfb2fb61770b2d034',
  wind:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_85a386be-84a3-4856-8663-c705b7414adb.jpeg?sign=1805254054-fd67ebfd36-0-561a080b448e3d79f8a5c7a94cb31333f665581cc56171939794e185cdb7bcc7',
  earth:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_0ea2d305-02d1-40b8-9a39-65239024d80a.jpeg?sign=1805254055-0e34b93db5-0-7ee738a75c6dd54f4b1beb94ed6037d4d571cabf6405ebf88eeb6a1666554132',
  heal:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_cbd88bf9-31c9-407b-aace-52ca01723730.jpeg?sign=1805254054-c7ca84e717-0-706d47823a0db9b1ec327521f3c83e5711a8fade7702ad64030498b48b3779d4',
  buff:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_962a1cc9-fbb0-401d-bf75-e315eb80c964.jpeg?sign=1805254058-8dd5b3bd0f-0-49ffc89cdc2c4c49cd446d602102bc034c51a085952faaf9f9489efe0042586b',
  critical:
    'https://coze-coding-project.tos.coze.site/coze_storage_7618056354904834098/image/generate_image_85449749-234f-483c-80f6-8540d911da60.jpeg?sign=1805254060-41aad3fc1a-0-6327e2001bb15a4788861fe8897f10461d83374565a539541d435b58b7d967a7',
} as const;

/** 获取角色立绘URL */
export function getCharacterIllustration(characterId: string): string {
  return (
    CHARACTER_ILLUSTRATIONS[characterId as keyof typeof CHARACTER_ILLUSTRATIONS] ||
    '/placeholder-character.png'
  );
}

/** 获取技能特效URL */
export function getSkillEffectUrl(element: string): string {
  return SKILL_EFFECTS[element as keyof typeof SKILL_EFFECTS] || SKILL_EFFECTS.fire;
}
