/* global Word */

/**
 * Office.js loads Word enums with the host-specific script (word-mac-*.js).
 * On Mac they may be missing until then — use string literals (documented API values).
 */
function pick(enumObj, key, literal) {
  try {
    if (enumObj && enumObj[key] != null) return enumObj[key];
  } catch {
    /* ignore */
  }
  return literal;
}

export const W = {
  unitCharacter: () => pick(Word?.Units, "character", "Character"),
  insertAfter: () => pick(Word?.InsertLocation, "after", "After"),
  insertReplace: () => pick(Word?.InsertLocation, "replace", "Replace"),
  insertEnd: () => pick(Word?.InsertLocation, "end", "End"),
  insertBefore: () => pick(Word?.InsertLocation, "before", "Before"),
  ccRichText: () => pick(Word?.ContentControlType, "richText", "RichText"),
  ccBoundingBox: () =>
    pick(Word?.ContentControlAppearance, "boundingBox", "BoundingBox"),
  ccTags: () => pick(Word?.ContentControlAppearance, "tags", "Tags"),
  ccHidden: () => pick(Word?.ContentControlAppearance, "hidden", "Hidden"),
  shapeAutoSizeNone: () => pick(Word?.ShapeAutoSize, "none", "None"),
  /** New paragraph — do not use inside kaeriten stacks (Word may wrap between paragraphs). */
  breakParagraph: () => pick(Word?.BreakType, "line", "Line"),
  /** Soft line break within one paragraph (Shift+Enter). */
  breakSoftLine: () => pick(Word?.BreakType, "lineBreak", "LineBreak"),
  rangeEnd: () => pick(Word?.RangeLocation, "end", "End"),
  rangeStart: () => pick(Word?.RangeLocation, "start", "Start"),
  rangeWhole: () => pick(Word?.RangeLocation, "whole", "Whole"),
  locBefore: () => pick(Word?.LocationRelation, "before", "Before"),
  locAfter: () => pick(Word?.LocationRelation, "after", "After"),
  locEqual: () => pick(Word?.LocationRelation, "equal", "Equal"),
  relHorizCharacter: () =>
    pick(Word?.RelativeHorizontalPosition, "character", "Character"),
  relVertLine: () => pick(Word?.RelativeVerticalPosition, "line", "Line"),
  wrapInline: () => pick(Word?.ShapeTextWrapType, "inline", "Inline"),
  wrapTight: () => pick(Word?.ShapeTextWrapType, "tight", "Tight"),
  alignLeft: () => pick(Word?.Alignment, "left", "Left"),
  alignCenter: () => pick(Word?.Alignment, "centered", "Centered"),
  alignRight: () => pick(Word?.Alignment, "right", "Right"),
  vertAlignTop: () =>
    pick(Word?.ShapeTextVerticalAlignment, "top", "Top"),
  vertAlignMiddle: () =>
    pick(Word?.ShapeTextVerticalAlignment, "middle", "Middle"),
  vertAlignBottom: () =>
    pick(Word?.ShapeTextVerticalAlignment, "bottom", "Bottom"),
  lineSpacingExactly: () =>
    pick(Word?.LineSpacingRule, "exactly", "Exactly"),
};

export function wordEnumsReady() {
  try {
    return (
      typeof Word !== "undefined" &&
      typeof Word.run === "function" &&
      (Word.InsertLocation != null || Word.insertLocation != null)
    );
  } catch {
    return false;
  }
}
