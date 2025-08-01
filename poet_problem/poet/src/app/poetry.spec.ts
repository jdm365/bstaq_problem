import { TestBed } from '@angular/core/testing';

import { Poetry } from './poetry';

describe('Poetry', () => {
  let service: Poetry;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Poetry);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
